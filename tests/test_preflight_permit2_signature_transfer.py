"""Adversarial angle (2026-06-08): preflight now covers Permit2's AllowanceTransfer transferFrom
(single 0x36c78516 + batch 0x0d58b1db) but NOT Permit2's *SignatureTransfer* interface — a DISTINCT
on-chain entrypoint that pulls tokens with a one-shot signed permit (no pre-existing allowance):

  permitTransferFrom(PermitTransferFrom, SignatureTransferDetails, owner, sig)            0x30f28b7a
  permitTransferFrom(PermitBatchTransferFrom, SignatureTransferDetails[], owner, sig)     0xedd9444b
  permitWitnessTransferFrom(..., bytes32 witness, string witnessType, sig)  single        0x137c29fe
  permitWitnessTransferFrom(..., batch)                                                   0xfe8ec1a7

The witness variants are exactly what intent/filler protocols (UniswapX, CowSwap) use. All of them
move `requestedAmount` of a token OUT of the signing owner TO `transferDetails.to` — a drain when `to`
is the attacker — yet they flowed through preflight as a single opaque LOW: ok=True, assert_safe PASSED
(empirically confirmed fail-OPEN). Same evasion CLASS as the AllowanceTransfer batch (this version),
the on-chain DAI permit (v0.5.22) and the Universal Router gap (v0.5.21): a covered drain shape via an
uncovered on-chain entrypoint. Fix: ABI-decode each variant's SignatureTransferDetails (arg index 1)
and emit token_transfer_from/HIGH for a non-empty transfer; an EMPTY batch moves nothing -> stays clean.
"""
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector as _sel
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
TOKEN = "0x" + "33" * 20
OWNER = "0x" + "11" * 20
PERMIT2 = "0x000000000022D473030F116dDEE9F6B43aC78BA3"

SIG_SINGLE = "permitTransferFrom(((address,uint256),uint256,uint256),(address,uint256),address,bytes)"
SIG_BATCH = "permitTransferFrom(((address,uint256)[],uint256,uint256),(address,uint256)[],address,bytes)"
SIG_WSINGLE = ("permitWitnessTransferFrom(((address,uint256),uint256,uint256),(address,uint256),"
               "address,bytes32,string,bytes)")
SIG_WBATCH = ("permitWitnessTransferFrom(((address,uint256)[],uint256,uint256),(address,uint256)[],"
              "address,bytes32,string,bytes)")


def _sel4(sig):
    return "0x" + _sel(sig).hex()


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _tx(data, to=PERMIT2):
    return {"to": to, "data": data, "value": 0}


def _single(recipient=ATTACKER, amount=10 ** 18):
    permit = ((TOKEN, amount), 0, 2 ** 48)
    details = (recipient, amount)
    return _sel4(SIG_SINGLE) + encode(
        ["((address,uint256),uint256,uint256)", "(address,uint256)", "address", "bytes"],
        [permit, details, OWNER, b""]).hex()


def _batch(details_list):
    permit = ([(TOKEN, 10 ** 18)], 0, 2 ** 48)
    return _sel4(SIG_BATCH) + encode(
        ["((address,uint256)[],uint256,uint256)", "(address,uint256)[]", "address", "bytes"],
        [permit, details_list, OWNER, b""]).hex()


def _wsingle(recipient=ATTACKER, amount=10 ** 18):
    permit = ((TOKEN, amount), 0, 2 ** 48)
    details = (recipient, amount)
    return _sel4(SIG_WSINGLE) + encode(
        ["((address,uint256),uint256,uint256)", "(address,uint256)", "address", "bytes32", "string", "bytes"],
        [permit, details, OWNER, b"\x00" * 32, "Witness(...)", b""]).hex()


def _wbatch(details_list):
    permit = ([(TOKEN, 10 ** 18)], 0, 2 ** 48)
    return _sel4(SIG_WBATCH) + encode(
        ["((address,uint256)[],uint256,uint256)", "(address,uint256)[]", "address", "bytes32", "string", "bytes"],
        [permit, details_list, OWNER, b"\x00" * 32, "Witness(...)", b""]).hex()


def test_signature_transfer_single_to_attacker_is_high():
    r = preflight(_tx(_single()))
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_signature_transfer_single_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_single()))


def test_signature_transfer_batch_is_high():
    r = preflight(_tx(_batch([(ATTACKER, 10 ** 18)])))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_signature_transfer_witness_single_is_high():
    # the variant UniswapX / CowSwap fillers use
    r = preflight(_tx(_wsingle()))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_signature_transfer_witness_batch_is_high():
    r = preflight(_tx(_wbatch([(ATTACKER, 10 ** 18)])))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_signature_transfer_wrapped_in_execute_is_high():
    inner = bytes.fromhex(_single()[2:])
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [PERMIT2, 0, inner]).hex()
    r = preflight(_tx(data, to="0x" + "44" * 20))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_signature_transfer_empty_batch_is_clean():
    r = preflight(_tx(_batch([])))
    assert "token_transfer_from" not in _codes(r)
    assert r["ok"] is True


def test_signature_transfer_malformed_does_not_crash():
    bad = _sel4(SIG_SINGLE) + "00" * 4
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r
