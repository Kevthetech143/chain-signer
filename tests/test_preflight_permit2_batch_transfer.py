"""Adversarial angle (2026-06-08): preflight covers the SINGLE on-chain Permit2 transferFrom
(transferFrom(address from,address to,uint160,address) = 0x36c78516) and the Universal-Router-wrapped
batch (PERMIT2_TRANSFER_FROM_BATCH command 0x0d), but NOT the DIRECT on-chain BATCH transferFrom on the
Permit2 contract itself: transferFrom((address,address,uint160,address)[]) = 0x0d58b1db. That entrypoint
writes the SAME drain — it pulls approved tokens OUT of one or more victims to the attacker — but its
amount/recipient live inside a dynamic tuple-array, so the flat fixed-offset decoder can't see it and
the call flows through as a single opaque LOW: ok=True, assert_safe PASSED (empirically confirmed
fail-OPEN). A drainer holding a batch of Permit2 allowances pulls from several tokens/victims in ONE
direct call and slips past.

Same evasion CLASS as the on-chain DAI permit (v0.5.22), the Universal Router gap (v0.5.21) and the
Permit2 permit-batch gap: a covered drain shape reachable through an uncovered on-chain entrypoint.
Fix: ABI-decode 0x0d58b1db's AllowanceTransferDetails[] and emit token_transfer_from/HIGH for a
non-empty batch. Non-noisy: an EMPTY batch moves nothing and must stay clean.
"""
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
TOKEN = "0x" + "33" * 20
TOKEN2 = "0x" + "55" * 20
VICTIM = "0x" + "11" * 20
VICTIM2 = "0x" + "22" * 20
PERMIT2 = "0x000000000022D473030F116dDEE9F6B43aC78BA3"

BATCH_SEL = "0x" + function_signature_to_4byte_selector(
    "transferFrom((address,address,uint160,address)[])").hex()


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _batch(details):
    # AllowanceTransferDetails[] = (from, to, amount, token)[]
    return BATCH_SEL + encode(["(address,address,uint160,address)[]"], [details]).hex()


def _tx(data, to=PERMIT2):
    return {"to": to, "data": data, "value": 0}


def test_permit2_batch_transfer_from_to_attacker_is_high():
    r = preflight(_tx(_batch([(VICTIM, ATTACKER, 10 ** 18, TOKEN)])))
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_permit2_batch_transfer_from_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_batch([(VICTIM, ATTACKER, 10 ** 18, TOKEN)])))


def test_permit2_batch_transfer_from_multi_victim_is_high():
    data = _batch([(VICTIM, ATTACKER, 10 ** 18, TOKEN), (VICTIM2, ATTACKER, 5 * 10 ** 18, TOKEN2)])
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_permit2_batch_transfer_wrapped_in_execute_is_high():
    inner = bytes.fromhex(_batch([(VICTIM, ATTACKER, 10 ** 18, TOKEN)])[2:])
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [PERMIT2, 0, inner]).hex()
    r = preflight(_tx(data, to="0x" + "44" * 20))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_permit2_batch_transfer_empty_is_clean():
    # an empty batch moves nothing — must NOT flag.
    r = preflight(_tx(_batch([])))
    assert "token_transfer_from" not in _codes(r)
    assert r["ok"] is True


def test_permit2_batch_transfer_malformed_does_not_crash():
    bad = BATCH_SEL + "00" * 4
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r
