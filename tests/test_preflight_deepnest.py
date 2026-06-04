"""Adversarial-review hardening (2026-06-03). A drain hidden in a multicall nested BEYOND the depth
cap was returning ok=True with only a MED advisory — so assert_safe() (the one-call hard stop most
integrators use) did NOT block it. A multicall nested deeper than the generous cap (5) is not a
legitimate pattern — no real dApp nests that deep — so it's a strong obfuscation/evasion signal, not
an innocent can't-decode. Refusing to unwrap an abnormally-deep nest must be HIGH so the hard stop
fires. Real multicalls nest 1-2 deep, so false-positive risk is near zero.
"""
from eth_abi import encode
import pytest
from chain_signer.preflight import preflight, assert_safe, _MAX_MULTICALL_DEPTH

ATTACKER = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
_MC = bytes.fromhex("ac9650d8")  # multicall(bytes[])


def _codes(r):
    return {(f["code"], f["severity"]) for f in r["risk_flags"]}


def _nested_approve(levels):
    inner = bytes.fromhex("095ea7b3") + bytes.fromhex(ATTACKER[2:].rjust(64, "0")) + b"\xff" * 32
    for _ in range(levels):
        inner = _MC + encode(["bytes[]"], [[inner]])
    return {"to": TOKEN, "data": "0x" + inner.hex(), "value": 0}


def test_deeply_nested_drain_is_high_and_blocks():
    r = preflight(_nested_approve(_MAX_MULTICALL_DEPTH + 1))  # past the cap
    assert any(sev == "HIGH" for _, sev in _codes(r))
    assert r["ok"] is False


def test_assert_safe_raises_on_deep_nest():
    with pytest.raises(ValueError):
        assert_safe(_nested_approve(_MAX_MULTICALL_DEPTH + 1))


def test_shallow_nested_drain_still_unwrapped_and_caught():
    # within the cap → fully unwrapped, the approval itself is the HIGH (not the depth refusal)
    r = preflight(_nested_approve(2))
    assert ("unlimited_approval", "HIGH") in _codes(r)
    assert r["ok"] is False
