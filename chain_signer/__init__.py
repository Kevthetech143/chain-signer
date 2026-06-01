"""chain-signer — non-custodial, multi-chain transaction tool for AI agents.

The calling agent holds its own private key. The key is generated/loaded locally and is
NEVER logged, serialized, or transmitted by this library. No MetaMask, no GUI.
"""
from .wallet import Wallet, create_wallet
from .api import to_wei, send_ether, burner, restore

__all__ = ["Wallet", "create_wallet", "to_wei", "send_ether", "burner", "restore"]
