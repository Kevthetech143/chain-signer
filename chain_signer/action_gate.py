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
    policy = policy if isinstance(policy, dict) else {}
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
        elif cap is not None and val > cap:
            v.append({"code": "value_over_limit",
                      "detail": f"value {val} wei exceeds the policy limit {cap} wei."})

    allow_recipients = policy.get("allow_recipients")
    if allow_recipients and "to" in args:
        to = (args.get("to") or "").lower()
        if to not in {str(a).lower() for a in allow_recipients}:
            v.append({"code": "recipient_not_allowed",
                      "detail": f"recipient {args.get('to')} is not on the allow-list."})

    return {"allowed": len(v) == 0, "violations": v}
