"""Red tests — sign_message helper (auth / sign-in-with-ethereum style flows).

Pure crypto, no network. Proves a message signed by a wallet recovers to that wallet's
address, closing the idiom gap customer #1 flagged (no Wallet.sign_message method).
"""
from eth_account import Account
from eth_account.messages import encode_defunct

from chain_signer import burner, sign_message


def test_sign_message_returns_0x_signature():
    w = burner()
    sig = sign_message(w, "hello agent")
    assert isinstance(sig, str) and sig.startswith("0x") and len(sig) == 132  # 65-byte sig hex


def test_signature_recovers_to_signer_address():
    w = burner()
    msg = "login nonce 12345"
    sig = sign_message(w, msg)
    recovered = Account.recover_message(encode_defunct(text=msg), signature=sig)
    assert recovered == w.address, "signed message did not recover to the wallet that signed it"


def test_different_wallets_produce_different_signatures():
    a, b = burner(), burner()
    assert sign_message(a, "same text") != sign_message(b, "same text")
