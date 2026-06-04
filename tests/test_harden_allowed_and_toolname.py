"""Adversarial-review hardening (2026-06-03). Two real false-negatives an attacker controls:

1. DAI-style permit `allowed` was matched with `is True` (strict identity). A hostile dApp builds the
   typed-data JSON it asks the agent to sign — it can send allowed=1 / "true" / "1" / "0x1", all of
   which decode to a true bool at the on-chain DAI verifier and grant an UNLIMITED allowance, while
   slipping past the guard. We must flag every encoding that means "true".

2. check_action forbid_tools lowercased but did not strip whitespace / normalize unicode, so a
   forbidden tool with a trailing newline/space (or look-alike) failed OPEN — while allow_tools fails
   CLOSED on the same input. The asymmetry favored the attacker. Both lists must normalize identically.
"""
from chain_signer.sig_inspect import inspect_typed_data
from chain_signer.action_gate import check_action

ATTACKER = "0x" + "ba" * 20


def _sig_codes(td):
    return {f["code"] for f in inspect_typed_data(td)["risk_flags"]}


def _dai(allowed):
    return {"primaryType": "Permit", "domain": {},
            "message": {"holder": "0x" + "11" * 20, "spender": ATTACKER,
                        "nonce": 0, "expiry": 0, "allowed": allowed}}


# --- Miss #1: DAI allowed encodings that all mean "true" ---
def test_dai_allowed_int_one_is_flagged():
    assert "unlimited_permit_signature" in _sig_codes(_dai(1))


def test_dai_allowed_str_true_is_flagged():
    assert "unlimited_permit_signature" in _sig_codes(_dai("true"))


def test_dai_allowed_str_one_is_flagged():
    assert "unlimited_permit_signature" in _sig_codes(_dai("1"))


def test_dai_allowed_hex_one_is_flagged():
    assert "unlimited_permit_signature" in _sig_codes(_dai("0x1"))


def test_dai_allowed_bool_true_still_flagged():
    assert "unlimited_permit_signature" in _sig_codes(_dai(True))


# false / 0 / "false" are NOT a grant — must NOT cry wolf
def test_dai_allowed_false_not_flagged():
    assert "unlimited_permit_signature" not in _sig_codes(_dai(False))


def test_dai_allowed_zero_not_flagged():
    assert "unlimited_permit_signature" not in _sig_codes(_dai(0))


def test_dai_allowed_str_false_not_flagged():
    assert "unlimited_permit_signature" not in _sig_codes(_dai("false"))


# --- Miss #2: forbid_tools must normalize whitespace/case like allow_tools ---
def test_forbid_tool_with_trailing_newline_is_denied():
    r = check_action({"tool": "send\n", "args": {}}, {"forbid_tools": ["send"]})
    assert r["allowed"] is False


def test_forbid_tool_with_surrounding_space_is_denied():
    r = check_action({"tool": "  bridge  ", "args": {}}, {"forbid_tools": ["bridge"]})
    assert r["allowed"] is False


def test_forbid_tool_uppercase_still_denied():
    r = check_action({"tool": "SEND", "args": {}}, {"forbid_tools": ["send"]})
    assert r["allowed"] is False


# a non-forbidden tool with whitespace is still allowed (no false positive)
def test_non_forbidden_tool_with_space_still_allowed():
    r = check_action({"tool": " read ", "args": {}}, {"forbid_tools": ["send"]})
    assert r["allowed"] is True
