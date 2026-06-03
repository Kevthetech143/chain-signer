"""chain-signer — non-custodial, multi-chain transaction tool for AI agents.

The calling agent holds its own private key. The key is generated/loaded locally and is
NEVER logged, serialized, or transmitted by this library. No MetaMask, no GUI.
"""
from .wallet import Wallet, create_wallet
from .api import (to_wei, send_ether, burner, restore, sign_message, sign_typed_data,
                  sign_x402_payment, export_encrypted, load_encrypted)
from .preflight import preflight, assert_safe
from .sig_inspect import inspect_typed_data

__all__ = ["Wallet", "create_wallet", "to_wei", "send_ether", "burner", "restore",
           "sign_message", "sign_typed_data", "sign_x402_payment", "export_encrypted", "load_encrypted",
           "preflight", "assert_safe", "inspect_typed_data"]
