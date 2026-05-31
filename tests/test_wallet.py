"""Red tests — non-custodial wallet + the key-secrecy invariant (the crown jewel).

Pure unit, no network. These pin BEHAVIOR, not implementation.
"""
import re

import pytest

from chain_signer import create_wallet

EVM_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
EVM_PRIVATE_KEY = re.compile(r"^0x[0-9a-fA-F]{64}$")  # 32-byte hex key


def test_create_wallet_returns_a_valid_evm_address():
    w = create_wallet("evm")
    assert EVM_ADDRESS.match(w.address), f"not a valid EVM address: {w.address!r}"


def test_each_new_wallet_is_unique():
    a = create_wallet("evm")
    b = create_wallet("evm")
    assert a.address != b.address, f"two fresh wallets shared an address: {a.address}"


def test_owner_can_read_their_own_private_key_as_a_32_byte_hex_key():
    # Non-custodial: the owner holds and can read their own key (to sign).
    w = create_wallet("evm")
    assert EVM_PRIVATE_KEY.match(w.private_key), f"private_key is not a 32-byte hex key: {w.private_key!r}"


def test_private_key_never_leaks_into_repr():
    w = create_wallet("evm")
    assert w.private_key not in repr(w), "private key leaked into repr()"


def test_private_key_never_leaks_into_str():
    w = create_wallet("evm")
    assert w.private_key not in str(w), "private key leaked into str()"


def test_public_info_is_exactly_address_and_chain():
    w = create_wallet("evm")
    info = w.public_info()
    assert info == {"address": w.address, "chain": "evm"}, f"public_info exposed unexpected fields: {info}"


def test_public_info_does_not_contain_the_private_key():
    w = create_wallet("evm")
    assert w.private_key not in str(w.public_info()), "private key leaked into public_info()"


def test_loading_the_same_key_yields_the_same_address():
    # An agent fully owns its wallet: restoring from its own key reproduces the address.
    w = create_wallet("evm")
    restored = create_wallet("evm", private_key=w.private_key)
    assert restored.address == w.address, f"restore-from-key changed address: {w.address} -> {restored.address}"


def test_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        create_wallet("dogecoin")
