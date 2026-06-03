"""Suite tool #2 — signed-message / permit-phishing inspector.

The off-chain scam the tx-preflight structurally can't catch: a dApp asks the agent to SIGN an
EIP-712 typed-data message (not a transaction). The classic drain is an ERC-2612 `permit` signature
granting an unlimited allowance to an attacker spender — the agent signs thinking it's a harmless
login, the attacker submits it on-chain and drains. inspect_typed_data() decodes the typed data and
flags the dangerous signature BEFORE the agent signs. Fail-safe: never raises.
"""
from chain_signer.sig_inspect import inspect_typed_data

OWNER = "0x" + "11" * 20
SPENDER = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
MAX = (1 << 256) - 1


def _permit_td(value):
    return {
        "types": {
            "EIP712Domain": [{"name": "name", "type": "string"}, {"name": "chainId", "type": "uint256"},
                             {"name": "verifyingContract", "type": "address"}],
            "Permit": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"},
                       {"name": "value", "type": "uint256"}, {"name": "nonce", "type": "uint256"},
                       {"name": "deadline", "type": "uint256"}],
        },
        "domain": {"name": "USD Coin", "chainId": 1, "verifyingContract": TOKEN},
        "primaryType": "Permit",
        "message": {"owner": OWNER, "spender": SPENDER, "value": str(value), "nonce": 0, "deadline": 9999999999},
    }


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_unlimited_erc2612_permit_signature_is_high():
    r = inspect_typed_data(_permit_td(MAX))
    assert "unlimited_permit_signature" in _codes(r)
    assert any(f["severity"] == "HIGH" for f in r["risk_flags"])
    assert r["ok"] is False


def test_large_permit_signature_is_med():
    r = inspect_typed_data(_permit_td(10 ** 25))   # large but not max
    assert "large_permit_signature" in _codes(r)
    assert r["ok"] is True   # MED only, no HIGH


def test_small_permit_signature_not_flagged():
    r = inspect_typed_data(_permit_td(1000))
    assert "unlimited_permit_signature" not in _codes(r)
    assert "large_permit_signature" not in _codes(r)
    assert r["ok"] is True


def test_non_dict_fails_safe():
    r = inspect_typed_data("not a dict")
    assert isinstance(r, dict) and r["ok"] is False
    assert "unparseable" in _codes(r)
