"""Adversarial angle (2026-06-06): the ON-CHAIN Permit2 surface was invisible to preflight.

Permit2 (Uniswap's universal approval contract, 0x000000000022D473030F116dDEE9F6B43aC78BA3) is now the
dominant approval path — most aggregators route ERC-20 approvals through it. Its calls are plain
transactions (they flow through preflight, NOT through the signed-message inspector), yet none of its
selectors were known to preflight:

  - AllowanceTransfer.approve(address token, address spender, uint160 amount, uint48 expiration) = 0x87517c45
  - AllowanceTransfer.transferFrom(address from, address to, uint160 amount, address token)       = 0x36c78516

So an agent granting an UNLIMITED Permit2 allowance, or executing a Permit2 drain pull, got only an
`opaque_calldata` LOW and ok=True — assert_safe would wave it through. Subtlety: Permit2 amount is
uint160, so "unlimited" is type(uint160).max, far below the ERC-20 1<<255 threshold; reusing the
ERC-20 check would miss it. These tests lock the fix.
"""
from eth_abi import encode
from chain_signer.preflight import preflight

TOKEN = "0x" + "11" * 20
SPENDER = "0x" + "22" * 20
FROM = "0x" + "33" * 20
TO = "0x" + "44" * 20

U160_MAX = (1 << 160) - 1
U48_MAX = (1 << 48) - 1


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _sev(r, code):
    return next(f["severity"] for f in r["risk_flags"] if f["code"] == code)


def _word(x):
    if isinstance(x, str):
        x = int(x, 16)
    return format(x, "064x")


def _permit2_approve(amount):
    # approve(address token, address spender, uint160 amount, uint48 expiration)
    return ("0x87517c45" + _word(TOKEN) + _word(SPENDER) + _word(amount) + _word(U48_MAX))


def test_permit2_unlimited_approval_is_high():
    r = preflight({"to": TOKEN, "data": _permit2_approve(U160_MAX), "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert _sev(r, "unlimited_approval") == "HIGH"
    assert r["ok"] is False
    # the SPENDER (3rd arg), not the token, must be named — proves correct arg offset
    detail = next(f["detail"] for f in r["risk_flags"] if f["code"] == "unlimited_approval")
    assert SPENDER[2:] in detail.lower()


def test_permit2_large_finite_approval_is_med():
    # 1e30 base units: large but not near uint160 max -> MED, not HIGH
    r = preflight({"to": TOKEN, "data": _permit2_approve(10 ** 30), "value": 0})
    assert "large_approval" in _codes(r)
    assert _sev(r, "large_approval") == "MED"


def test_permit2_small_approval_not_flagged_high():
    # a normal, bounded approval must NOT trip the unlimited/large flags
    r = preflight({"to": TOKEN, "data": _permit2_approve(1000), "value": 0})
    assert "unlimited_approval" not in _codes(r)
    assert "large_approval" not in _codes(r)


def test_permit2_transfer_from_is_high():
    # transferFrom(address from, address to, uint160 amount, address token) = 0x36c78516
    data = ("0x36c78516" + _word(FROM) + _word(TO) + _word(U160_MAX) + _word(TOKEN))
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "token_transfer_from" in _codes(r)
    assert _sev(r, "token_transfer_from") == "HIGH"
    assert r["ok"] is False
    detail = next(f["detail"] for f in r["risk_flags"] if f["code"] == "token_transfer_from")
    assert FROM[2:] in detail.lower() and TO[2:] in detail.lower()


def test_permit2_unlimited_approval_hidden_in_multicall_is_high():
    inner = bytes.fromhex(_permit2_approve(U160_MAX)[2:])
    data = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False
