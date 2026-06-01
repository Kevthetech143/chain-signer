"""Red tests — encrypted key storage (Security pillar V1.1 must-fix).

So an agent can store its key at rest as a password-protected keystore instead of a plain
string. Reuses eth_account's audited keystore (Account.encrypt/decrypt). Pure crypto, no network.
"""
import json
import pytest

from chain_signer import burner, export_encrypted, load_encrypted


def test_export_encrypted_round_trips_to_same_address():
    w = burner()
    ks = export_encrypted(w, "correct horse battery staple")
    back = load_encrypted(ks, "correct horse battery staple")
    assert back.address == w.address, "decrypted keystore did not reproduce the wallet"


def test_keystore_does_not_contain_the_plaintext_key():
    w = burner()
    ks = export_encrypted(w, "pw123")
    blob = json.dumps(ks)
    assert w.private_key[2:].lower() not in blob.lower(), "plaintext key leaked into keystore!"


def test_wrong_password_is_rejected():
    w = burner()
    ks = export_encrypted(w, "right-pw")
    with pytest.raises(Exception):
        load_encrypted(ks, "wrong-pw")
