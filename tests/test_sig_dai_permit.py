"""DAI-style permit — a different EIP-712 permit shape that the value-based check misses.

DAI's permit is permit(holder, spender, nonce, expiry, allowed: bool). There is NO `value` field;
`allowed: true` grants an UNLIMITED allowance. A check that only reads `value` waves a DAI permit
straight through — a real gap, since DAI is a major token. allowed:true must be flagged HIGH.
"""
from chain_signer.sig_inspect import inspect_typed_data

HOLDER = "0x" + "11" * 20
SPENDER = "0x" + "22" * 20
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"


def _dai_permit(allowed):
    return {
        "types": {"Permit": [{"name": "holder", "type": "address"}, {"name": "spender", "type": "address"},
                             {"name": "nonce", "type": "uint256"}, {"name": "expiry", "type": "uint256"},
                             {"name": "allowed", "type": "bool"}]},
        "domain": {"name": "Dai Stablecoin", "chainId": 1, "verifyingContract": DAI},
        "primaryType": "Permit",
        "message": {"holder": HOLDER, "spender": SPENDER, "nonce": 0, "expiry": 0, "allowed": allowed},
    }


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_dai_permit_allowed_true_is_high():
    r = inspect_typed_data(_dai_permit(True))
    assert "unlimited_permit_signature" in _codes(r) and r["ok"] is False


def test_dai_permit_allowed_false_not_flagged():
    # allowed:false REVOKES — that's safe, must not cry wolf
    r = inspect_typed_data(_dai_permit(False))
    assert "unlimited_permit_signature" not in _codes(r) and r["ok"] is True
