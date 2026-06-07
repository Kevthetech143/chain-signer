"""Permit2 SignatureTransfer (PermitTransferFrom / PermitBatchTransferFrom) — the transfer-auth mode.

We already cover Permit2 allowance permits (PermitSingle/Batch). SignatureTransfer is the other mode:
the signature authorizes a spender to pull `permitted.amount` of a token. Legit apps (Uniswap swaps)
use the EXACT amount — so flagging large-but-exact would cry wolf. We flag ONLY an effectively
UNLIMITED permitted amount (the phishing tell), HIGH. Specific/large amounts are NOT flagged.
"""
from chain_signer.sig_inspect import inspect_typed_data

SP = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
U160_MAX = (1 << 160) - 1


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _single(amount):
    return {"primaryType": "PermitTransferFrom", "domain": {},
            "message": {"permitted": {"token": TOKEN, "amount": str(amount)}, "spender": SP, "nonce": 0, "deadline": 9999999999}}


def test_permit2_signature_transfer_unlimited_is_high():
    r = inspect_typed_data(_single(U160_MAX))
    assert "unlimited_permit_signature" in _codes(r) and r["ok"] is False


def test_permit2_signature_transfer_exact_amount_not_flagged():
    # a real swap authorizes an exact amount — must NOT cry wolf
    r = inspect_typed_data(_single(1500 * 10 ** 6))
    assert "unlimited_permit_signature" not in _codes(r) and r["ok"] is True


def test_permit2_batch_transfer_unlimited_is_high():
    td = {"primaryType": "PermitBatchTransferFrom", "domain": {},
          "message": {"permitted": [{"token": TOKEN, "amount": str(1000)}, {"token": TOKEN, "amount": str(U160_MAX)}],
                      "spender": SP, "nonce": 0, "deadline": 9999999999}}
    assert "unlimited_permit_signature" in _codes(inspect_typed_data(td))


def test_permit2_witness_transfer_unlimited_is_high():
    """Evasion: an attacker swaps PermitTransferFrom for its WITNESS variant
    (PermitWitnessTransferFrom — used by intent protocols like UniswapX). It carries the IDENTICAL
    `permitted{token,amount}` shape, so an unlimited amount is the same signature-transfer drain — yet
    the dispatch only matched the non-witness names, so it fell through with ok=True (fail-OPEN). Same
    evasion class as the v0.5.9/0.5.10 Permit2 approve->permit swap: a covered entrypoint dodged by
    picking an uncovered name that writes the same state."""
    td = {"primaryType": "PermitWitnessTransferFrom", "domain": {},
          "message": {"permitted": {"token": TOKEN, "amount": str(U160_MAX)}, "spender": SP,
                      "nonce": 0, "deadline": 9999999999, "witness": "0x" + "00" * 32}}
    r = inspect_typed_data(td)
    assert "unlimited_permit_signature" in _codes(r) and r["ok"] is False


def test_permit2_batch_witness_transfer_unlimited_is_high():
    td = {"primaryType": "PermitBatchWitnessTransferFrom", "domain": {},
          "message": {"permitted": [{"token": TOKEN, "amount": str(1000)}, {"token": TOKEN, "amount": str(U160_MAX)}],
                      "spender": SP, "nonce": 0, "deadline": 9999999999}}
    r = inspect_typed_data(td)
    assert "unlimited_permit_signature" in _codes(r) and r["ok"] is False


def test_permit2_witness_transfer_exact_amount_not_flagged():
    # a real witness transfer (intent order) authorizes an exact amount — must NOT cry wolf
    td = {"primaryType": "PermitWitnessTransferFrom", "domain": {},
          "message": {"permitted": {"token": TOKEN, "amount": str(1500 * 10 ** 6)}, "spender": SP,
                      "nonce": 0, "deadline": 9999999999, "witness": "0x" + "00" * 32}}
    r = inspect_typed_data(td)
    assert "unlimited_permit_signature" not in _codes(r) and r["ok"] is True
