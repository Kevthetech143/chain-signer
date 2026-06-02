"""Red test — an unlimited approval hidden inside multicall(bytes[]) must still be caught.
Routers batch calls via multicall; a drainer can bury an infinite approve in there."""
from eth_abi import encode
from chain_signer.preflight import preflight

SP = "0x" + "11" * 20


def _inner_approve(amount):
    return bytes.fromhex("095ea7b3" + SP[2:].rjust(64, "0") + format(amount, "064x"))


def _multicall(inner_calls):
    # multicall(bytes[]) selector 0xac9650d8
    return "0xac9650d8" + encode(["bytes[]"], [inner_calls]).hex()


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_unlimited_approve_inside_multicall_is_caught():
    tx = {"to": "0x" + "22" * 20, "data": _multicall([_inner_approve((1 << 256) - 1)]), "value": 0}
    r = preflight(tx)
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_clean_multicall_not_flagged():
    tx = {"to": "0x" + "22" * 20, "data": _multicall([_inner_approve(100 * 10**6)]), "value": 0}
    r = preflight(tx)
    assert "unlimited_approval" not in _codes(r)
