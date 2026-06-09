"""Adversarial angle (2026-06-09): preflight unwraps ERC-4337 execute/executeBatch and Gnosis Safe
multiSend (0x8d80ff0a), but NOT the Safe's PRIMARY entrypoint — execTransaction (0x6a761202). Every
Gnosis Safe transaction is submitted through execTransaction(to, value, data, operation, ...): the real
inner call the multisig runs lives in the `data` arg (index 2). A drain wrapped one layer down —
execTransaction(token, 0, approve(attacker, MAX), ...) — flowed through preflight as a single opaque
LOW: ok=True, assert_safe PASSED (empirically confirmed fail-OPEN). A Safe-owning agent reviewing its
own multisig tx before co-signing got a false all-clear.

Same evasion CLASS as the Universal Router gap (v0.5.21), the on-chain DAI permit (v0.5.22), the
Permit2 AllowanceTransfer batch (v0.5.23) and the Permit2 SignatureTransfer pull (v0.5.24): a covered
drain shape reachable through an uncovered on-chain entrypoint. Fix: treat execTransaction as a wrapper
and recurse into its `data` arg (which also reaches the common Safe -> multiSend -> drain path). A Safe
tx with empty data moves no tokens -> stays clean; a benign inner call stays clean.
"""
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector as _sel
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
TOKEN = "0x" + "33" * 20
SAFE = "0x" + "44" * 20
ZERO = "0x" + "00" * 20
MAX = 2 ** 256 - 1

SIG = "execTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes)"


def _sel4(sig):
    return "0x" + _sel(sig).hex()


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _tx(data, to=SAFE):
    return {"to": to, "data": data, "value": 0}


def _exec(inner_data, to=TOKEN, value=0, operation=0):
    inner = bytes.fromhex(inner_data[2:]) if isinstance(inner_data, str) else inner_data
    return _sel4(SIG) + encode(
        ["address", "uint256", "bytes", "uint8", "uint256", "uint256", "uint256", "address", "address", "bytes"],
        [to, value, inner, operation, 0, 0, 0, ZERO, ZERO, b""]).hex()


def _approve(spender=ATTACKER, amount=MAX):
    return "0x095ea7b3" + encode(["address", "uint256"], [spender, amount]).hex()


def _transfer_from(frm=SAFE, to=ATTACKER, amount=10 ** 18):
    return "0x23b872dd" + encode(["address", "address", "uint256"], [frm, to, amount]).hex()


def test_safe_exec_unlimited_approve_is_high():
    r = preflight(_tx(_exec(_approve())))
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_safe_exec_unlimited_approve_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_exec(_approve())))


def test_safe_exec_transfer_from_is_high():
    r = preflight(_tx(_exec(_transfer_from())))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_safe_exec_wrapping_multisend_drain_is_high():
    # the real-world path: Safe execTransaction -> multiSend -> inner approve drain
    ms_inner = bytes.fromhex(_approve()[2:])
    # one multiSend record: operation(1)=00, to(20), value(32)=0, len(32), data
    rec = b"\x00" + bytes.fromhex(TOKEN[2:]) + (0).to_bytes(32, "big") + len(ms_inner).to_bytes(32, "big") + ms_inner
    multisend = "0x8d80ff0a" + encode(["bytes"], [rec]).hex()
    r = preflight(_tx(_exec(multisend, to="0x" + "55" * 20, operation=1)))
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_safe_exec_empty_data_is_clean():
    # a Safe ETH transfer carries empty inner data -> moves no tokens -> must NOT flag a drain
    r = preflight(_tx(_exec(b"", to=ATTACKER, value=10 ** 18)))
    assert "unlimited_approval" not in _codes(r)
    assert "token_transfer_from" not in _codes(r)


def test_safe_exec_benign_inner_stays_clean():
    # exact (non-unlimited) approve of a small amount inside a Safe tx is not a drain flag
    r = preflight(_tx(_exec(_approve(amount=1000))))
    assert "unlimited_approval" not in _codes(r)


def test_safe_exec_malformed_does_not_crash():
    bad = _sel4(SIG) + "00" * 4
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r
