"""Action-policy gate — enforce allow/forbid rules before an agent acts.

The identity layer answers "who is this agent." It does NOT answer "should this agent be allowed to
DO this." Every agent-identity vendor + NIST (2026) named that gap: auth isn't enough, you must
inspect the action. check_action() evaluates a proposed action (a tool call) against a policy and
returns {allowed, violations} BEFORE it runs. Deterministic, offline, never raises. Fail-safe:
unreadable input is DENIED (a policy gate that errors open is worse than useless).

policy keys (all optional; absent = not enforced):
  forbid_tools: [str]        — tool names that are never allowed
  allow_tools: [str]         — if set, ONLY these tools are allowed
  max_value_wei: int         — cap on args.value_wei (EVM native value)
  allow_recipients: [str]    — if set, args.to must be one of these (case-insensitive)
"""
from .preflight import _to_int


def check_action(action, policy=None):
    """Return {"allowed": bool, "violations": [{"code","detail"}]}. Never raises."""
    if not isinstance(action, dict):
        return {"allowed": False, "violations": [{"code": "unparseable",
                "detail": "action is not a readable object — denying (a policy gate must fail closed)."}]}
    # policy=None is the documented "no policy" default (no constraints). But a non-None policy that
    # isn't a dict is UNREADABLE — a misconfigured gate. Fail CLOSED rather than silently allowing
    # everything (a policy gate that errors open is worse than useless). Matches the action-side rule.
    if policy is None:
        policy = {}
    elif not isinstance(policy, dict):
        return {"allowed": False, "violations": [{"code": "unparseable_policy",
                "detail": "policy is not a readable object — denying (a policy gate must fail closed)."}]}
    tool = action.get("tool")
    # Normalize the candidate tool the SAME way on both lists — a guard must not be defeated by
    # trailing whitespace / casing. forbid_tools previously failed OPEN on "send\n" while allow_tools
    # failed CLOSED; that asymmetry favored the attacker. Callers must dispatch on the normalized name.
    tool_l = tool.strip().casefold() if isinstance(tool, str) else tool
    args = action.get("args") if isinstance(action.get("args"), dict) else {}
    v = []

    # allow_tools: an EXPLICIT empty list means "allow nothing" — must fail closed, not open.
    # (use `is not None`, not truthiness). Tool matching is case/whitespace-insensitive.
    allow_tools = policy.get("allow_tools")
    if allow_tools is not None:
        allowed_set = {str(t).strip().casefold() for t in allow_tools}
        if tool_l not in allowed_set:
            v.append({"code": "tool_not_allowed",
                      "detail": f"tool '{tool}' is not in the allow-list {list(allow_tools)}."})
    forbid_set = {str(t).strip().casefold() for t in (policy.get("forbid_tools") or [])}
    if tool_l in forbid_set:
        v.append({"code": "forbidden_tool", "detail": f"tool '{tool}' is forbidden by policy."})

    if policy.get("max_value_wei") is not None and "value_wei" in args:
        val = _to_int(args.get("value_wei"))
        cap = _to_int(policy.get("max_value_wei"))
        if val is None:
            v.append({"code": "unreadable_value", "detail": "action value_wei can't be read — denying."})
        elif cap is None:
            # The operator SET a value cap (max_value_wei is not None) but it can't be read — e.g.
            # typo'd as "1 ETH". Skipping the check would silently disable the limit and allow any
            # value (fail-OPEN). A cap that can't be read must DENY, like every other unreadable input.
            v.append({"code": "unreadable_value_limit",
                      "detail": "policy max_value_wei is set but unreadable — denying (a value cap that "
                                "can't be read must fail closed)."})
        elif val > cap:
            v.append({"code": "value_over_limit",
                      "detail": f"value {val} wei exceeds the policy limit {cap} wei."})

    # A recipient allow-list means the operator cares WHERE funds go, so it must FAIL CLOSED — like
    # allow_tools. The old `if allow_recipients and "to" in args` skipped the check when `to` was
    # absent, ALLOWING a value-bearing action with no recipient (a fail-open that defeats the list);
    # and `(args.get("to") or "").lower()` RAISED on a non-string `to` (breaks the never-raises
    # contract). Now: check a readable `to` against the list; otherwise deny when `to` is present-but-
    # unreadable OR the action moves native value (a transfer we can't verify). A pure non-value
    # action with no `to` isn't a transfer, so it is not flagged (stay non-noisy).
    allow_recipients = policy.get("allow_recipients")
    if allow_recipients:
        allowed_recips = {str(a).strip().lower() for a in allow_recipients}
        to_raw = args.get("to")
        to = to_raw.strip().lower() if isinstance(to_raw, str) else None
        if to is not None:
            if to not in allowed_recips:
                v.append({"code": "recipient_not_allowed",
                          "detail": f"recipient {args.get('to')} is not on the allow-list."})
        else:
            val = _to_int(args.get("value_wei"))
            moves_value = val is not None and val > 0
            if "to" in args or moves_value:
                v.append({"code": "recipient_not_allowed",
                          "detail": "action has no readable recipient to check against the allow-list "
                                    "(missing or unreadable `to` on a value transfer) — denying "
                                    "(a recipient allow-list must fail closed)."})

    return {"allowed": len(v) == 0, "violations": v}
