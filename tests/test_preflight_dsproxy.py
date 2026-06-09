"""Adversarial angle (2026-06-09): preflight unwraps ERC-4337 execute, Gnosis Safe execTransaction/
multiSend, multicall and the Universal Router — but NOT DSProxy, the delegatecall proxy nearly every
MakerDAO / Oasis / InstaDapp user action routes through. A DSProxy holds the user's approvals and
delegatecalls whatever `data` you hand it:

  execute(address target, bytes data)  -> delegatecall `data` at `target`           (0x1cff79cd)
  execute(bytes code,     bytes data)  -> deploy `code`, then delegatecall `data`    (0x1f6a1eb9)

In BOTH overloads the REAL inner call is the trailing `bytes data` arg. An unlimited approve() (or a
transferFrom drain) wrapped one layer down in execute() flowed through preflight as a single opaque
LOW: ok=True, only ['opaque_calldata'] (empirically confirmed fail-OPEN this fire). An agent operating
its DSProxy, asked to approve an attacker or pull its balance out, got a false all-clear.

Same evasion CLASS as Universal Router (v0.5.21), DAI on-chain permit (v0.5.22), Permit2 batch
transferFrom (v0.5.23), Permit2 SignatureTransfer (v0.5.24), Gnosis Safe execTransaction (v0.5.25)
and ERC-777 operator (v0.5.26): a covered drain shape reached through an uncovered wrapper. The fix
recurses into the `data` arg exactly like execute()/execTransaction, so a benign DSProxy call (clean
swap, exact approval) stays clean and only the inner call's real effect is judged.
"""
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector as _sel
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
VICTIM = "0x" + "44" * 20
TOKEN = "0x" + "33" * 20
PROXY = "0x" + "55" * 20
ZERO = "0x" + "00" * 20
MAX = 2 ** 256 - 1

APPROVE = "0x095ea7b3"
TRANSFER_FROM = "0x23b872dd"
EXEC_ADDR_BYTES = "0x1cff79cd"     # execute(address,bytes)
EXEC_BYTES_BYTES = "0x1f6a1eb9"    # execute(bytes,bytes)


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _tx(data, to=PROXY):
    return {"to": to, "data": data, "value": 0}


def _unlimited_approve(spender=ATTACKER):
    return APPROVE + encode(["address", "uint256"], [spender, MAX]).hex()


def _transfer_from(frm=VICTIM, to=ATTACKER, amount=10 ** 18):
    return TRANSFER_FROM + encode(["address", "address", "uint256"], [frm, to, amount]).hex()


def _exec_addr(inner_hex, target=TOKEN):
    inner = bytes.fromhex(inner_hex[2:])
    return EXEC_ADDR_BYTES + encode(["address", "bytes"], [target, inner]).hex()


def _exec_code(inner_hex, code=b"\x60\x60"):
    inner = bytes.fromhex(inner_hex[2:])
    return EXEC_BYTES_BYTES + encode(["bytes", "bytes"], [code, inner]).hex()


def test_dsproxy_wrapping_unlimited_approve_is_high():
    r = preflight(_tx(_exec_addr(_unlimited_approve())))
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_dsproxy_wrapping_unlimited_approve_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_exec_addr(_unlimited_approve())))


def test_dsproxy_wrapping_transfer_from_is_high():
    r = preflight(_tx(_exec_addr(_transfer_from())))
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_dsproxy_execute_bytes_bytes_wrapping_drain_is_high():
    r = preflight(_tx(_exec_code(_unlimited_approve())))
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_dsproxy_wrapping_benign_call_stays_clean():
    # an exact (non-unlimited) approve inside DSProxy must NOT trip the unlimited flag
    exact = APPROVE + encode(["address", "uint256"], [ATTACKER, 10 ** 18]).hex()
    r = preflight(_tx(_exec_addr(exact)))
    assert "unlimited_approval" not in _codes(r)
    assert r["ok"] is True


def test_dsproxy_wrapping_plain_transfer_stays_clean():
    # a normal ETH-less ERC-20 transfer of a small amount carries no HIGH flag
    transfer = "0xa9059cbb" + encode(["address", "uint256"], [ATTACKER, 10 ** 18]).hex()
    r = preflight(_tx(_exec_addr(transfer)))
    assert r["ok"] is True


def test_dsproxy_drain_wrapped_in_multicall_is_high():
    # the evasion-class check: a DSProxy drain reached through a covered wrapper still flags
    inner = bytes.fromhex(_exec_addr(_unlimited_approve())[2:])
    data = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight(_tx(data))
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_dsproxy_wrapping_exectransaction_drain_is_high():
    # nested the other way: DSProxy execute wrapping a Safe execTransaction wrapping the approve
    sig = "execTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes)"
    approve = bytes.fromhex(_unlimited_approve()[2:])
    safe = "0x" + _sel(sig).hex() + encode(
        ["address", "uint256", "bytes", "uint8", "uint256", "uint256", "uint256", "address", "address", "bytes"],
        [TOKEN, 0, approve, 0, 0, 0, 0, ZERO, ZERO, b""]).hex()
    r = preflight(_tx(_exec_addr(safe, target=PROXY)))
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_dsproxy_malformed_does_not_crash():
    bad = EXEC_ADDR_BYTES + "00" * 2
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r


def test_dsproxy_empty_data_does_not_flag_drain():
    # execute(target, "") delegatecalls nothing dangerous -> no drain flag
    data = EXEC_ADDR_BYTES + encode(["address", "bytes"], [TOKEN, b""]).hex()
    r = preflight(_tx(data))
    assert "unlimited_approval" not in _codes(r)
    assert "token_transfer_from" not in _codes(r)
