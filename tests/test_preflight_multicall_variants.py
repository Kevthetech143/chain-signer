"""v0.2.4 only caught the bare multicall(bytes[]) selector. Real routers use other multicall
shapes — Uniswap V3/V4 routers use multicall(uint256 deadline, bytes[]) and
multicall(bytes32, bytes[]) — and a drainer can nest a multicall inside a multicall. Both
slipped past. The inner-decode must cover every multicall variant AND recurse.
"""
from eth_abi import encode
from chain_signer.preflight import preflight

SP = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
MAX = (1 << 256) - 1


def _approve(amount):
    return bytes.fromhex("095ea7b3" + SP[2:].rjust(64, "0") + format(amount, "064x"))


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_uniswap_deadline_multicall_uint256_bytes():
    # multicall(uint256 deadline, bytes[] data) = 0x5ae401dc
    data = "0x5ae401dc" + encode(["uint256", "bytes[]"], [9999999999, [_approve(MAX)]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_blockhash_multicall_bytes32_bytes():
    # multicall(bytes32 previousBlockhash, bytes[] data) = 0x1f0464d1
    data = "0x1f0464d1" + encode(["bytes32", "bytes[]"], [b"\x00" * 32, [_approve(MAX)]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_nested_multicall_is_caught():
    inner = bytes.fromhex("ac9650d8" + encode(["bytes[]"], [[_approve(MAX)]]).hex())
    outer = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight({"to": TOKEN, "data": outer, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_clean_uniswap_multicall_not_flagged():
    data = "0x5ae401dc" + encode(["uint256", "bytes[]"], [9999999999, [_approve(1000)]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" not in _codes(r)
