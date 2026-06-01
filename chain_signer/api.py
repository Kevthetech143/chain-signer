"""V1 developer-facing facade — think in ETH, send in one call.

Thin layer over the unit-tested engine: create_wallet (wallet.py) + send_live (live.py).
Builders pass ether amounts; we convert to integer wei exactly and let send_live fetch
nonce/gas and broadcast. Non-custodial throughout — the agent's key never leaves send().
"""
from decimal import Decimal

from .live import DEFAULT_CHAIN_ID, send_live
from .wallet import create_wallet

WEI_PER_ETHER = 10**18


def burner(chain="evm", *, testnet=False):
    """Make a fresh throwaway wallet for one task. The agent holds the key; discard when done.

    Same call as create_wallet() with no key — named for the burner-per-task pattern.
    """
    return create_wallet(chain, testnet=testnet)


def restore(private_key, chain="evm", *, testnet=False):
    """Reload a wallet from its exported private key. Same key -> same address (deterministic)."""
    return create_wallet(chain, private_key=private_key, testnet=testnet)


def to_wei(amount_ether) -> int:
    """Exact ether -> integer wei. Accepts int, float, str, or Decimal without float drift."""
    return int(Decimal(str(amount_ether)) * WEI_PER_ETHER)


def sign_message(wallet, text: str) -> str:
    """Sign a plain-text message with the wallet's key (EIP-191 personal_sign).

    Returns the 0x signature hex. Recoverable via eth_account Account.recover_message.
    For auth / sign-in-with-ethereum style flows. EVM wallets only.
    """
    from eth_account import Account
    from eth_account.messages import encode_defunct
    signed = Account.sign_message(encode_defunct(text=text), private_key=wallet.private_key)
    return signed.signature.to_0x_hex()


def send_ether(wallet, to, amount_ether, *, chain="evm", chain_id=DEFAULT_CHAIN_ID, fetch=None):
    """One-call send: convert ether->wei, fetch nonce+gas, sign with the owner's key, broadcast.

    Returns the send_live result dict ({"hash", "raw", ...}). RPC is injectable via `fetch`.
    """
    return send_live(wallet, to, to_wei(amount_ether), chain=chain, chain_id=chain_id, fetch=fetch)
