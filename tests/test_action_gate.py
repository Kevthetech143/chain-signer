"""Suite tool #3 — action-policy gate.

"Authentication isn't enough — you must inspect what the agent DOES" (every identity vendor + NIST,
2026). check_action() evaluates a proposed agent action (a tool call) against a policy and returns
allow/deny + reasons, BEFORE the action runs. Deterministic, offline, never raises. The enforcement
layer the identity stacks don't provide.
"""
from chain_signer.action_gate import check_action

RECIP = "0x" + "aa" * 20
OTHER = "0x" + "bb" * 20


def _codes(r):
    return {v["code"] for v in r["violations"]}


def test_forbidden_tool_is_denied():
    action = {"tool": "bridge", "args": {}}
    r = check_action(action, {"forbid_tools": ["bridge", "swap"]})
    assert r["allowed"] is False and "forbidden_tool" in _codes(r)


def test_allowed_tool_passes():
    r = check_action({"tool": "send", "args": {"to": RECIP, "value_wei": 100}}, {"forbid_tools": ["bridge"]})
    assert r["allowed"] is True and r["violations"] == []


def test_value_over_limit_is_denied():
    action = {"tool": "send", "args": {"to": RECIP, "value_wei": 5 * 10**18}}
    r = check_action(action, {"max_value_wei": 10**18})
    assert r["allowed"] is False and "value_over_limit" in _codes(r)


def test_unreadable_value_cap_fails_closed():
    """Fail-open: the operator sets a value cap but typos it as a non-numeric string. The cap can't be
    read (cap is None), so the old code SKIPPED the comparison and ALLOWED a large transfer — silently
    disabling the limit the operator asked for. A value cap that can't be read must DENY, like every
    other unreadable input in this gate (same class as the v0.5.8 malformed-policy fail-open)."""
    action = {"tool": "send", "args": {"to": RECIP, "value_wei": 10**18}}
    r = check_action(action, {"max_value_wei": "1 ETH"})
    assert r["allowed"] is False and "unreadable_value_limit" in _codes(r)


def test_readable_cap_under_limit_still_passes():
    # the fix must not over-deny: a readable cap with an in-bounds value stays allowed
    action = {"tool": "send", "args": {"to": RECIP, "value_wei": 10**16}}
    r = check_action(action, {"max_value_wei": 10**17})
    assert r["allowed"] is True


def test_recipient_not_on_allowlist_is_denied():
    action = {"tool": "send", "args": {"to": OTHER, "value_wei": 1}}
    r = check_action(action, {"allow_recipients": [RECIP]})
    assert r["allowed"] is False and "recipient_not_allowed" in _codes(r)


def test_recipient_on_allowlist_passes():
    action = {"tool": "send", "args": {"to": RECIP, "value_wei": 1}}
    r = check_action(action, {"allow_recipients": [RECIP]})
    assert r["allowed"] is True


def test_no_policy_allows_but_flags_open():
    r = check_action({"tool": "send", "args": {}}, {})
    assert r["allowed"] is True


def test_bad_input_fails_safe_denied():
    r = check_action("not an action", {"forbid_tools": ["x"]})
    assert r["allowed"] is False and "unparseable" in _codes(r)


# --- Adversarial (2026-06-06): the recipient allow-list must FAIL CLOSED, mirroring allow_tools. ---

def test_recipient_allowlist_value_transfer_with_no_to_is_denied():
    """A recipient allow-list means the operator cares WHERE funds go. An action that MOVES native
    value but omits `to` entirely cannot be verified against the list — the old code skipped the check
    (`if allow_recipients and "to" in args`) and ALLOWED it: a fail-OPEN that defeats the whole point
    of a recipient whitelist. A value-bearing action with no readable recipient must DENY."""
    action = {"tool": "send", "args": {"value_wei": 5 * 10**17}}   # 0.5 ETH, no `to`
    r = check_action(action, {"allow_recipients": [RECIP]})
    assert r["allowed"] is False and "recipient_not_allowed" in _codes(r)


def test_recipient_allowlist_nonvalue_action_with_no_to_not_flagged():
    """Conservative: a NON-value action (no value_wei) with no `to` isn't a transfer, so a recipient
    allow-list shouldn't force a recipient on it — don't cry wolf on a read-only/no-transfer tool call."""
    r = check_action({"tool": "get_balance", "args": {}}, {"allow_recipients": [RECIP]})
    assert "recipient_not_allowed" not in _codes(r)


def test_recipient_allowlist_nonstring_to_does_not_crash():
    """A hostile/buggy caller controls args; a non-string `to` (int/list/dict) must not raise —
    check_action's contract is 'never raises'. Old code did `(args.get("to") or "").lower()` which
    threw AttributeError on a non-string. Unreadable recipient on a value action => fail closed."""
    action = {"tool": "send", "args": {"to": 12345, "value_wei": 5 * 10**17}}
    r = check_action(action, {"allow_recipients": [RECIP]})   # must not raise
    assert r["allowed"] is False and "recipient_not_allowed" in _codes(r)
