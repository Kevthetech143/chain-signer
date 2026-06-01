"""V1 developer-facing facade — think in ETH, send in one call.

Thin layer over the unit-tested engine: create_wallet (wallet.py) + send_live (live.py).
Builders pass ether amounts; we convert to integer wei exactly and let send_live fetch
nonce/gas and broadcast. Non-custodial throughout — the agent's key never leaves send().
"""
from decimal import Decimal

from .live import DEFAULT_CHAIN_ID, send_live

WEI_PER_ETHER = 10**18


def to_wei(amount_ether) -> int:
    """Exact ether -> integer wei. Accepts int, float, str, or Decimal without float drift."""
    return int(Decimal(str(amount_ether)) * WEI_PER_ETHER)


def send_ether(wallet, to, amount_ether, *, chain="evm", chain_id=DEFAULT_CHAIN_ID, fetch=None):
    """One-call send: convert ether->wei, fetch nonce+gas, sign with the owner's key, broadcast.

    Returns the send_live result dict ({"hash", "raw", ...}). RPC is injectable via `fetch`.
    """
    return send_live(wallet, to, to_wei(amount_ether), chain=chain, chain_id=chain_id, fetch=fetch)
