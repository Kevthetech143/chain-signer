"""Red tests — burner ergonomics: throwaway-per-task wallet + export/restore round-trip.

Pure unit, no network. burner() makes a fresh wallet you can discard; restore() reloads it
from its exported private key. Non-custodial: the key is the only thing needed to restore.
"""
import base58

from chain_signer import burner, restore


def test_burner_makes_a_fresh_evm_wallet():
    w = burner()
    assert w.chain == "evm"
    assert w.address.startswith("0x") and len(w.address) == 42


def test_each_burner_is_unique():
    assert burner().address != burner().address


def test_burner_round_trips_via_exported_key_evm():
    w = burner()
    again = restore(w.private_key)
    assert again.address == w.address, "restore from exported key did not reproduce the address"


def test_restore_defaults_to_evm():
    w = burner()
    assert restore(w.private_key).chain == "evm"


def test_burner_round_trips_on_solana():
    w = burner("solana")
    assert len(base58.b58decode(w.address)) == 32
    again = restore(w.private_key, "solana")
    assert again.address == w.address, "solana burner did not restore to same address"
