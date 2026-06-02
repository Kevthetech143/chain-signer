"""Red tests — EIP-712 typed-data signing, the piece x402 agent payments actually need.

Demand-verified (2026-06-01 hunt): agents paying x402 APIs sign typed data / EIP-3009
authorizations, not plain text. We shipped only EIP-191 (sign_message). This pins a
sign_typed_data(wallet, domain, types, message) helper whose signature recovers to the signer.
"""
from eth_account import Account
from eth_account.messages import encode_typed_data

from chain_signer import burner, sign_typed_data

DOMAIN = {"name": "ChainSigner", "version": "1", "chainId": 137,
          "verifyingContract": "0x" + "00" * 20}
TYPES = {"Mail": [{"name": "contents", "type": "string"}]}
MESSAGE = {"contents": "pay 0.10 USDC for this API call"}


def test_sign_typed_data_returns_hex_signature():
    sig = sign_typed_data(burner(), DOMAIN, TYPES, MESSAGE)
    assert isinstance(sig, str) and sig.startswith("0x") and len(sig) == 132


def test_typed_signature_recovers_to_the_signer():
    w = burner()
    sig = sign_typed_data(w, DOMAIN, TYPES, MESSAGE)
    recovered = Account.recover_message(
        encode_typed_data(domain_data=DOMAIN, message_types=TYPES, message_data=MESSAGE),
        signature=sig,
    )
    assert recovered == w.address


def test_different_message_changes_signature():
    w = burner()
    a = sign_typed_data(w, DOMAIN, TYPES, {"contents": "a"})
    b = sign_typed_data(w, DOMAIN, TYPES, {"contents": "b"})
    assert a != b
