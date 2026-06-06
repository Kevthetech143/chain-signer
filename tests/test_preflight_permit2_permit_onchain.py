"""Adversarial angle (2026-06-06): the v0.5.9 Permit2 fix had a trivial BYPASS.

v0.5.9 taught preflight to flag the on-chain Permit2 AllowanceTransfer.approve() (0x87517c45) as an
unlimited-allowance grant. But Permit2 has a SECOND on-chain entrypoint that grants the exact same
allowance — permit():

  AllowanceTransfer.permit(address owner, PermitSingle, bytes sig)  = 0x2b67b570
  AllowanceTransfer.permit(address owner, PermitBatch,  bytes sig)  = 0x2a2d80d1

where PermitSingle = ((address token, uint160 amount, uint48 expiration, uint48 nonce), address
spender, uint256 sigDeadline). Submitting a permit() on-chain consumes a signed permit and writes the
SAME (spender -> unlimited uint160 allowance) state that approve() writes. So an attacker who handed an
agent a permit() tx instead of an approve() tx fully bypassed the v0.5.9 guard: it returned only
opaque_calldata LOW + ok=True, and assert_safe waved it through. Flagging approve but not permit is an
inconsistency, not a real guard. These tests lock the fix.

Subtlety: the amount lives INSIDE a tuple (single) or a tuple-array (batch), so it can't be read at a
fixed flat word offset for the batch form — it needs real ABI decoding. uint160 "infinite" is
type(uint160).max, far below the ERC-20 1<<255 threshold (reuses the v0.5.9 _UNLIMITED_U160 rule).
"""
from eth_abi import encode
from chain_signer.preflight import preflight

TOKEN = "0x" + "11" * 20
SPENDER = "0x" + "22" * 20
OWNER = "0x" + "99" * 20

U160_MAX = (1 << 160) - 1
U48_MAX = (1 << 48) - 1
U256_MAX = (1 << 256) - 1

_SINGLE = ["address", "((address,uint160,uint48,uint48),address,uint256)", "bytes"]
_BATCH = ["address", "((address,uint160,uint48,uint48)[],address,uint256)", "bytes"]


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _sev(r, code):
    return next(f["severity"] for f in r["risk_flags"] if f["code"] == code)


def _detail(r, code):
    return next(f["detail"] for f in r["risk_flags"] if f["code"] == code)


def _permit_single(amount, spender=SPENDER, token=TOKEN):
    details = (token, amount, U48_MAX, 0)
    permit_single = (details, spender, U256_MAX)
    body = encode(_SINGLE, [OWNER, permit_single, b"\x00" * 65])
    return "0x2b67b570" + body.hex()


def _permit_batch(amounts, spender=SPENDER, token=TOKEN):
    details = [(token, a, U48_MAX, 0) for a in amounts]
    permit_batch = (details, spender, U256_MAX)
    body = encode(_BATCH, [OWNER, permit_batch, b"\x00" * 65])
    return "0x2a2d80d1" + body.hex()


def test_permit2_permit_single_unlimited_is_high():
    r = preflight({"to": "0x" + "00" * 19 + "01", "data": _permit_single(U160_MAX), "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert _sev(r, "unlimited_approval") == "HIGH"
    assert r["ok"] is False
    # the SPENDER (not the token) must be named — proves the tuple was decoded at the right field
    assert SPENDER[2:] in _detail(r, "unlimited_approval").lower()


def test_permit2_permit_single_large_finite_is_med():
    r = preflight({"to": TOKEN, "data": _permit_single(10 ** 30), "value": 0})
    assert "large_approval" in _codes(r)
    assert _sev(r, "large_approval") == "MED"
    assert "unlimited_approval" not in _codes(r)


def test_permit2_permit_single_small_not_flagged():
    r = preflight({"to": TOKEN, "data": _permit_single(1000), "value": 0})
    assert "unlimited_approval" not in _codes(r)
    assert "large_approval" not in _codes(r)


def test_permit2_permit_batch_any_unlimited_is_high():
    # a bounded entry AND an unlimited entry sharing one spender -> still HIGH
    r = preflight({"to": TOKEN, "data": _permit_batch([1000, U160_MAX]), "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert _sev(r, "unlimited_approval") == "HIGH"
    assert r["ok"] is False


def test_permit2_permit_batch_all_small_not_flagged():
    r = preflight({"to": TOKEN, "data": _permit_batch([100, 2000]), "value": 0})
    assert "unlimited_approval" not in _codes(r)
    assert "large_approval" not in _codes(r)


def test_permit2_permit_single_unlimited_hidden_in_multicall_is_high():
    inner = bytes.fromhex(_permit_single(U160_MAX)[2:])
    data = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False
