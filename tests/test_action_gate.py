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
