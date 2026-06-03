"""Permit2 (Uniswap) signature-phishing — the other half of off-chain permit drains.

Permit2 amounts are uint160, so its "unlimited" sentinel ((2**160)-1) is BELOW preflight's uint256
threshold — a naive check misses it. inspect_typed_data must use a Permit2-specific threshold.
PermitSingle (one token) and PermitBatch (a list) both carry a spender + per-token amount.
"""
from chain_signer.sig_inspect import inspect_typed_data

SPENDER = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
PERMIT2 = "0x000000000022D473030F116dDEE9F6B43aC78BA3"
U160_MAX = (1 << 160) - 1


def _permit_single(amount):
    return {
        "types": {"PermitSingle": [{"name": "details", "type": "PermitDetails"},
                                   {"name": "spender", "type": "address"},
                                   {"name": "sigDeadline", "type": "uint256"}]},
        "domain": {"name": "Permit2", "chainId": 1, "verifyingContract": PERMIT2},
        "primaryType": "PermitSingle",
        "message": {"details": {"token": TOKEN, "amount": str(amount), "expiration": 281474976710655, "nonce": 0},
                    "spender": SPENDER, "sigDeadline": 9999999999},
    }


def _permit_batch(amounts):
    return {
        "types": {"PermitBatch": [{"name": "details", "type": "PermitDetails[]"},
                                  {"name": "spender", "type": "address"},
                                  {"name": "sigDeadline", "type": "uint256"}]},
        "domain": {"name": "Permit2", "chainId": 1, "verifyingContract": PERMIT2},
        "primaryType": "PermitBatch",
        "message": {"details": [{"token": TOKEN, "amount": str(a), "expiration": 0, "nonce": 0} for a in amounts],
                    "spender": SPENDER, "sigDeadline": 9999999999},
    }


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_permit2_single_unlimited_is_high():
    r = inspect_typed_data(_permit_single(U160_MAX))
    assert "unlimited_permit_signature" in _codes(r) and r["ok"] is False


def test_permit2_batch_unlimited_is_high():
    r = inspect_typed_data(_permit_batch([1000, U160_MAX]))   # one clean, one unlimited
    assert "unlimited_permit_signature" in _codes(r) and r["ok"] is False


def test_permit2_single_small_not_flagged():
    r = inspect_typed_data(_permit_single(1000))
    assert "unlimited_permit_signature" not in _codes(r) and r["ok"] is True
