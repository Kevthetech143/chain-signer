"""ERC-2612 permit() submitted as a transaction grants an allowance on-chain — a drainer can
call permit(owner, attacker, MAX, ...) then transferFrom. This is the ON-CHAIN permit CALL
(has calldata), distinct from the OFF-CHAIN EIP-712 signature case that stays out of scope.
"""
from chain_signer.preflight import preflight

OWNER = "0x" + "11" * 20
SPENDER = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
MAX = (1 << 256) - 1


def _permit(spender, value):
    # permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s)
    words = [
        OWNER[2:].rjust(64, "0"),
        spender[2:].rjust(64, "0"),
        format(value, "064x"),
        format(0, "064x"),          # deadline
        format(27, "064x"),         # v
        "00" * 32,                  # r
        "00" * 32,                  # s
    ]
    return "0xd505accf" + "".join(words)


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_unlimited_permit_is_high():
    r = preflight({"to": TOKEN, "data": _permit(SPENDER, MAX), "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_small_permit_not_flagged():
    r = preflight({"to": TOKEN, "data": _permit(SPENDER, 1000), "value": 0})
    assert "unlimited_approval" not in _codes(r)
    assert "large_approval" not in _codes(r)
