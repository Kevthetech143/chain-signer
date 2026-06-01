"""Red tests — Bitcoin wallet via chain dispatch (non-custodial), mainnet + testnet."""
from chain_signer import create_wallet


def test_create_bitcoin_wallet_address_and_chain():
    w = create_wallet("bitcoin")
    assert w.chain == "bitcoin"
    assert w.address[0] == "1", f"expected mainnet P2PKH address: {w.address}"


def test_each_bitcoin_wallet_is_unique():
    assert create_wallet("bitcoin").address != create_wallet("bitcoin").address


def test_owner_can_read_their_wif_key():
    w = create_wallet("bitcoin")
    assert w.private_key[0] in "KL5", f"not a mainnet WIF: {w.private_key[:1]}"


def test_bitcoin_key_never_leaks():
    w = create_wallet("bitcoin")
    assert w.private_key not in repr(w)
    assert w.private_key not in str(w)
    assert w.private_key not in str(w.public_info())


def test_bitcoin_public_info_is_exactly_address_and_chain():
    w = create_wallet("bitcoin")
    assert w.public_info() == {"address": w.address, "chain": "bitcoin"}


def test_restore_bitcoin_from_wif_yields_same_address():
    w = create_wallet("bitcoin")
    assert create_wallet("bitcoin", private_key=w.private_key).address == w.address


def test_testnet_bitcoin_wallet():
    w = create_wallet("bitcoin", testnet=True)
    assert w.address[0] in "mn" or w.address.startswith("tb1"), f"not a testnet address: {w.address}"
    assert w.private_key[0] == "c", f"not a testnet WIF: {w.private_key[:1]}"
