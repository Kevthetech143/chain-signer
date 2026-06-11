"""Multicall3 (0xcA11bde05977b3631167028862bE2a173976CA11 — the same address on every EVM chain)
is the most-deployed batch helper in the ecosystem, and agents routinely batch through it. Its
aggregate/aggregate3 entrypoints do NOT carry a flat bytes[] like the Uniswap multicall variants —
each inner call is a TUPLE (Call/Call3/Call3Value) whose calldata is one field. v0.5.28 only
unwrapped the flat bytes[] shape, so an unlimited approve hidden in an aggregate3 tuple slipped
through with only a LOW opaque flag (proven by adversarial probe 2026-06-11). The inner-decode must
extract the calldata field from each tuple and recurse, exactly as it does for multicall(bytes[]).
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


def test_aggregate3_hides_unlimited_approval():
    # aggregate3((address target, bool allowFailure, bytes callData)[]) = 0x82ad56cb
    data = "0x82ad56cb" + encode(["(address,bool,bytes)[]"], [[(TOKEN, False, _approve(MAX))]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_aggregate3value_hides_unlimited_approval():
    # aggregate3Value((address,bool,uint256 value,bytes callData)[]) = 0x174dea71
    data = "0x174dea71" + encode(
        ["(address,bool,uint256,bytes)[]"], [[(TOKEN, False, 0, _approve(MAX))]]
    ).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_legacy_aggregate_hides_unlimited_approval():
    # aggregate((address target, bytes callData)[]) = 0x252dba42 (Multicall/Multicall2 + Multicall3)
    data = "0x252dba42" + encode(["(address,bytes)[]"], [[(TOKEN, _approve(MAX))]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_tryaggregate_hides_unlimited_approval():
    # tryAggregate(bool requireSuccess, (address,bytes)[]) = 0xbce38bd7 — calls is the 2nd arg
    data = "0xbce38bd7" + encode(["bool", "(address,bytes)[]"], [True, [(TOKEN, _approve(MAX))]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_aggregate3_multiple_calls_flags_the_drain_among_clean():
    # a clean call batched alongside the drain — the drain must still surface
    data = "0x82ad56cb" + encode(
        ["(address,bool,bytes)[]"],
        [[(TOKEN, False, _approve(1000)), (TOKEN, False, _approve(MAX))]],
    ).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_clean_aggregate3_not_flagged():
    # an exact-amount approve batched through aggregate3 must NOT trip the unlimited flag
    data = "0x82ad56cb" + encode(["(address,bool,bytes)[]"], [[(TOKEN, False, _approve(1000))]]).hex()
    r = preflight({"to": TOKEN, "data": data, "value": 0})
    assert "unlimited_approval" not in _codes(r)
