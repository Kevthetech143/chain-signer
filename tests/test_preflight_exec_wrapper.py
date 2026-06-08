"""Adversarial angle (2026-06-07): preflight recursed into multicall variants but NOT into the
ERC-4337 / smart-account execute wrappers. An agent's smart wallet (ERC-4337 account, Gnosis Safe)
does not call approve()/transferFrom() directly — it routes EVERY action through `execute()` /
`executeBatch()` (ERC-4337) or `multiSend()` (Safe). So a drain wrapped one layer down —
`execute(token, 0, approve(attacker, MAX))` — flowed through preflight as a single opaque LOW call:
ok=True, assert_safe PASSED (empirically confirmed fail-OPEN). This is the dominant calldata shape
in our exact niche (AI agents signing for their own smart accounts), same evasion CLASS as the
v0.5.5 multicall recursion gap — a covered drain hidden behind an uncovered wrapper selector.

Fix: decode the wrappers and recurse into their inner call(s) via the existing depth-capped
_collect_flags path. Non-noisy by construction: we flag only on what the INNER call is — a benign
execute (clean swap, exact approval, empty data ETH transfer) stays clean exactly as today.
"""
from eth_abi import encode
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
TOKEN = "0x" + "33" * 20
SAFE = "0x" + "44" * 20
MAX = (1 << 256) - 1


def _approve(amount, spender=ATTACKER):
    return bytes.fromhex("095ea7b3" + spender[2:].rjust(64, "0") + format(amount, "064x"))


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


# --- ERC-4337 execute(address,uint256,bytes) = 0xb61d27f6 ---

def test_execute_wrapping_unlimited_approve_is_high():
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [TOKEN, 0, _approve(MAX)]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_execute_wrapping_unlimited_approve_hard_stops():
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [TOKEN, 0, _approve(MAX)]).hex()
    with pytest.raises(ValueError):
        assert_safe({"to": SAFE, "data": data, "value": 0})


def test_execute_wrapping_transferfrom_is_high():
    inner = bytes.fromhex("23b872dd" + ("0x" + "11" * 20)[2:].rjust(64, "0")
                          + ATTACKER[2:].rjust(64, "0") + format(1, "064x"))
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [TOKEN, 0, inner]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


# --- ERC-4337 executeBatch(address[],uint256[],bytes[]) = 0x47e1da2a ---

def test_execute_batch_3arg_wrapping_drain_is_high():
    data = "0x47e1da2a" + encode(["address[]", "uint256[]", "bytes[]"],
                                  [[TOKEN], [0], [_approve(MAX)]]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


# --- ERC-4337 executeBatch(address[],bytes[]) = 0x18dfb3c7 ---

def test_execute_batch_2arg_wrapping_drain_is_high():
    data = "0x18dfb3c7" + encode(["address[]", "bytes[]"], [[TOKEN], [_approve(MAX)]]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


# --- Gnosis Safe multiSend(bytes) = 0x8d80ff0a (packed encoding) ---

def _multisend_packed(calls):
    """calls = [(to_hex, value_int, data_bytes)]; pack op(1)+to(20)+value(32)+len(32)+data."""
    blob = b""
    for to, value, d in calls:
        blob += (b"\x00"                                   # operation = CALL
                 + bytes.fromhex(to[2:])
                 + value.to_bytes(32, "big")
                 + len(d).to_bytes(32, "big")
                 + d)
    return "0x8d80ff0a" + encode(["bytes"], [blob]).hex()


def test_multisend_wrapping_drain_is_high():
    data = _multisend_packed([(TOKEN, 0, _approve(MAX))])
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_multisend_drain_among_clean_calls_is_high():
    clean = _approve(1000)
    data = _multisend_packed([(TOKEN, 0, clean), (TOKEN, 0, _approve(MAX))])
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


# --- Non-noisy: a benign execute must NOT be flagged ---

def test_execute_wrapping_exact_approval_not_flagged():
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [TOKEN, 0, _approve(1000)]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" not in _codes(r)
    assert r["ok"] is True


def test_execute_empty_inner_data_eth_transfer_not_flagged():
    # execute(recipient, 1 ETH, "") — a plain native transfer, nothing to unwrap; must stay clean.
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [ATTACKER, 10 ** 18, b""]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert r["ok"] is True


def test_execute_malformed_inner_does_not_crash():
    bad = "0xb61d27f6" + "00" * 4    # truncated wrapper args
    r = preflight({"to": SAFE, "data": bad, "value": 0})
    assert isinstance(r, dict) and "risk_flags" in r


# --- Cross-wrapper nesting (depth-2): a smart account routes execute() whose inner calldata is
# itself a multicall bundling the drain (and the inverse). The single-depth tests above don't cover
# this realistic ERC-4337 batch shape; lock that the recursion is symmetric across wrapper kinds. ---

def _multicall(calls):
    """multicall(bytes[]) = 0xac9650d8 wrapping a list of inner-call byte strings."""
    return bytes.fromhex("ac9650d8" + encode(["bytes[]"], [calls]).hex())


def test_execute_wrapping_multicall_wrapping_drain_is_high():
    inner = "0x" + _multicall([_approve(MAX)]).hex()
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"],
                                  [TOKEN, 0, bytes.fromhex(inner[2:])]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_multicall_wrapping_execute_wrapping_drain_is_high():
    execute = bytes.fromhex("b61d27f6" + encode(["address", "uint256", "bytes"],
                                                [TOKEN, 0, _approve(MAX)]).hex())
    data = "0x" + _multicall([execute]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_execute_batch_2arg_flags_every_call_in_batch():
    tf = bytes.fromhex("23b872dd" + ("0x" + "12" * 20)[2:].rjust(64, "0")
                       + ATTACKER[2:].rjust(64, "0") + format(1, "064x"))
    data = "0x18dfb3c7" + encode(["address[]", "bytes[]"],
                                 [[TOKEN, TOKEN], [_approve(MAX), tf]]).hex()
    r = preflight({"to": SAFE, "data": data, "value": 0})
    assert {"unlimited_approval", "token_transfer_from"} <= _codes(r) and r["ok"] is False
