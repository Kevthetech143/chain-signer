"""Red tests — non-custodial wallet + the key-secrecy invariant (the crown jewel).

Pure unit, no network. These pin BEHAVIOR, not implementation.
"""
import re

import pytest

from chain_signer import create_wallet

EVM_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")


def test_create_wallet_returns_a_valid_evm_address():
    w = create_wallet("evm")
    assert EVM_ADDRESS.match(w.address), f"not a valid EVM address: {w.address!r}"


def test_each_new_wallet_is_unique():
    a = create_wallet("evm")
    b = create_wallet("evm")
    assert a.address != b.address


def test_owner_can_access_their_private_key():
    # Non-custodial: the owner holds and can read their own key (to sign).
    w = create_wallet("evm")
    assert isinstance(w.private_key, str) and len(w.private_key) > 0


def test_private_key_never_leaks_into_repr_or_str():
    w = create_wallet("evm")
    assert w.private_key not in repr(w)
    assert w.private_key not in str(w)


def test_public_info_excludes_the_private_key():
    w = create_wallet("evm")
    info = w.public_info()
    assert "address" in info
    assert w.private_key not in str(info)
    assert all("priv" not in k.lower() for k in info.keys())


def test_loading_same_key_yields_same_address():
    # An agent fully owns its wallet: restoring from its own key reproduces the address.
    w = create_wallet("evm")
    restored = create_wallet("evm", private_key=w.private_key)
    assert restored.address == w.address


def test_unsupported_chain_raises_clear_error():
    with pytest.raises(ValueError):
        create_wallet("dogecoin")
