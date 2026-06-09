"""Adversarial angle (2026-06-09): preflight covers the ERC-20/721 approve+transferFrom drain family
and Permit2, but NOT ERC-777's operator model — the SAME drain shape on a different token standard.
ERC-777 (used by real tokens: imBTC, pNetwork pTokens, some wrapped assets) lets a holder name an
"operator" that can move ALL their tokens:

  authorizeOperator(operator)                  -> operator gains full control of every ERC-777 token
                                                  the caller holds (the setApprovalForAll-equivalent).
  operatorSend(from, to, amount, data, opData) -> the operator's pull-to-attacker (the transferFrom-
                                                  equivalent drain-execution call).

Both flowed through preflight as a single opaque LOW: ok=True, only ['opaque_calldata'] (empirically
confirmed fail-OPEN this fire). An agent holding an ERC-777 token, asked to authorize an attacker as
operator or to operatorSend its balance out, got a false all-clear.

Same evasion CLASS as Universal Router (v0.5.21), DAI on-chain permit (v0.5.22), Permit2 batch
transferFrom (v0.5.23), Permit2 SignatureTransfer (v0.5.24) and Gnosis Safe execTransaction (v0.5.25):
a covered drain shape reachable through an uncovered entrypoint. operatorBurn is deliberately NOT
flagged here — it destroys tokens (no recipient/attacker), not a drain-to-attacker. revokeOperator
REMOVES control -> safe.
"""
from eth_abi import encode
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
VICTIM = "0x" + "44" * 20
TOKEN = "0x" + "33" * 20
SAFE = "0x" + "44" * 20
ZERO = "0x" + "00" * 20
MAX = 2 ** 256 - 1

AUTHORIZE = "0x959b8c3f"          # authorizeOperator(address)
OPERATOR_SEND = "0x62ad1b83"      # operatorSend(address,address,uint256,bytes,bytes)
REVOKE = "0xfad8b32a"             # revokeOperator(address)
OPERATOR_BURN = "0xfc673c4f"      # operatorBurn(address,uint256,bytes,bytes)


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _tx(data, to=TOKEN):
    return {"to": to, "data": data, "value": 0}


def _authorize(operator=ATTACKER):
    return AUTHORIZE + encode(["address"], [operator]).hex()


def _operator_send(frm=VICTIM, to=ATTACKER, amount=10 ** 18):
    return OPERATOR_SEND + encode(
        ["address", "address", "uint256", "bytes", "bytes"], [frm, to, amount, b"", b""]).hex()


def test_authorize_operator_is_high():
    r = preflight(_tx(_authorize()))
    assert "approval_for_all" in _codes(r)
    assert r["ok"] is False


def test_authorize_operator_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_authorize()))


def test_operator_send_is_high():
    r = preflight(_tx(_operator_send()))
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_operator_send_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_operator_send()))


def test_revoke_operator_is_not_a_drain_flag():
    # revoking an operator REMOVES control -> must not flag a grant/drain
    r = preflight(_tx(REVOKE + encode(["address"], [ATTACKER]).hex()))
    assert "approval_for_all" not in _codes(r)
    assert "token_transfer_from" not in _codes(r)


def test_operator_burn_is_not_a_transfer_flag():
    # operatorBurn destroys tokens (no recipient) -> not a drain-to-attacker
    burn = OPERATOR_BURN + encode(["address", "uint256", "bytes", "bytes"], [VICTIM, 10 ** 18, b"", b""]).hex()
    r = preflight(_tx(burn))
    assert "token_transfer_from" not in _codes(r)


def test_authorize_operator_wrapped_in_exectransaction_is_high():
    # the evasion-class check: a covered drain reached through a covered wrapper still flags
    sig = "execTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes)"
    from eth_utils import function_signature_to_4byte_selector as _sel
    inner = bytes.fromhex(_authorize()[2:])
    data = "0x" + _sel(sig).hex() + encode(
        ["address", "uint256", "bytes", "uint8", "uint256", "uint256", "uint256", "address", "address", "bytes"],
        [TOKEN, 0, inner, 0, 0, 0, 0, ZERO, ZERO, b""]).hex()
    r = preflight(_tx(data, to=SAFE))
    assert "approval_for_all" in _codes(r)
    assert r["ok"] is False


def test_operator_send_wrapped_in_multicall_is_high():
    inner = bytes.fromhex(_operator_send()[2:])
    data = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_erc777_malformed_does_not_crash():
    bad = AUTHORIZE + "00" * 2
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r
