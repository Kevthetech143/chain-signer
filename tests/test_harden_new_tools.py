"""Adversarial-review fixes (2026-06-03) for the two newest suite tools.

(a) action_gate: an explicit empty allow_tools [] must DENY everything (a gate that must fail closed
    treated [] as "no allowlist" = fail-open). And tool-name matching must be case-insensitive.
(b) sig_inspect: permit primaryType matching must be case/whitespace-robust — a security tool
    shouldn't be defeated by "permit"/"Permit "/"permitsingle".
"""
from chain_signer.action_gate import check_action
from chain_signer.sig_inspect import inspect_typed_data

SPENDER = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
MAX = (1 << 256) - 1
U160_MAX = (1 << 160) - 1


def _vcodes(r):
    return {v["code"] for v in r["violations"]}


# --- action_gate ---
def test_empty_allow_tools_denies_everything():
    r = check_action({"tool": "drain", "args": {}}, {"allow_tools": []})
    assert r["allowed"] is False and "tool_not_allowed" in _vcodes(r)


def test_forbid_tools_is_case_insensitive():
    r = check_action({"tool": "Bridge", "args": {}}, {"forbid_tools": ["bridge"]})
    assert r["allowed"] is False and "forbidden_tool" in _vcodes(r)


# --- sig_inspect: primaryType robustness ---
def _scodes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_lowercase_permit_still_flagged():
    td = {"primaryType": "permit", "domain": {},
          "message": {"spender": SPENDER, "value": str(MAX)}}
    assert "unlimited_permit_signature" in _scodes(inspect_typed_data(td))


def test_permit_with_trailing_space_flagged():
    td = {"primaryType": "Permit ", "domain": {},
          "message": {"spender": SPENDER, "value": str(MAX)}}
    assert "unlimited_permit_signature" in _scodes(inspect_typed_data(td))


def test_lowercase_permitsingle_flagged():
    td = {"primaryType": "permitsingle", "domain": {},
          "message": {"details": {"token": TOKEN, "amount": U160_MAX}, "spender": SPENDER}}
    assert "unlimited_permit_signature" in _scodes(inspect_typed_data(td))
