"""Red tests — Solana wallet via chain dispatch (non-custodial), plus EVM regression guard.

Pure unit, no network. Solana address = base58 of a 32-byte pubkey; key = base58 of the 64-byte secret.
"""
import base58
import pytest

from chain_signer import create_wallet


def test_create_solana_wallet_returns_a_valid_address():
    w = create_wallet("solana")
    assert len(base58.b58decode(w.address)) == 32, f"solana pubkey not 32 bytes: {w.address}"
    assert w.chain == "solana"


def test_each_solana_wallet_is_unique():
    assert create_wallet("solana").address != create_wallet("solana").address


def test_solana_owner_can_read_their_key():
    w = create_wallet("solana")
    assert len(base58.b58decode(w.private_key)) == 64, "solana secret key should be 64 bytes"


def test_solana_key_never_leaks_into_repr_str_or_public_info():
    w = create_wallet("solana")
    assert w.private_key not in repr(w)
    assert w.private_key not in str(w)
    assert w.private_key not in str(w.public_info())


def test_solana_public_info_is_exactly_address_and_chain():
    w = create_wallet("solana")
    assert w.public_info() == {"address": w.address, "chain": "solana"}


def test_restore_solana_from_key_yields_same_address():
    w = create_wallet("solana")
    restored = create_wallet("solana", private_key=w.private_key)
    assert restored.address == w.address


def test_evm_wallet_still_works_after_adding_solana():
    w = create_wallet("evm")
    assert w.chain == "evm" and w.address.startswith("0x") and len(w.address) == 42
