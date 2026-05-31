"""Live adapter — fetch nonce + gas and broadcast, so signing functions can run on a real network.

Uses the Etherscan v2 proxy JSON-RPC (read truth + broadcast). HTTP is injectable for tests.
This is the glue that turns the unit-tested send() into a one-call live send. GREEN STEP fills this in.
"""
from .tx import send

DEFAULT_CHAIN_ID = 137  # Polygon mainnet (use 80002 for Amoy testnet)


def get_nonce(address, *, chain_id=DEFAULT_CHAIN_ID, fetch=None):
    raise NotImplementedError("green step")


def get_gas_fees(*, chain_id=DEFAULT_CHAIN_ID, fetch=None):
    raise NotImplementedError("green step")


def make_broadcaster(*, chain_id=DEFAULT_CHAIN_ID, fetch=None):
    raise NotImplementedError("green step")


def send_live(wallet, to, value_wei, *, chain="evm", chain_id=DEFAULT_CHAIN_ID, fetch=None):
    """Fetch nonce + gas, sign with the owner's key, and broadcast. Returns the send() result."""
    raise NotImplementedError("green step")
