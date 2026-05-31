"""Live adapter — fetch nonce + gas and broadcast, so signing functions can run on a real network.

Uses the Etherscan v2 proxy JSON-RPC (read truth + broadcast). HTTP is injectable for tests.
This is the glue that turns the unit-tested send() into a one-call live send.
"""
import os
from urllib.parse import urlencode

from .balance import ETHERSCAN_V2_BASE, _default_fetch
from .tx import _addr, send

DEFAULT_CHAIN_ID = 137  # Polygon mainnet (use 80002 for Amoy testnet)


def _proxy(action_params, chain_id, fetch):
    params = {"chainid": int(chain_id), "module": "proxy", **action_params,
              "apikey": os.environ.get("ETHERSCAN_API_KEY", "")}
    return (fetch or _default_fetch)(ETHERSCAN_V2_BASE + "?" + urlencode(params))


def get_nonce(address, *, chain_id=DEFAULT_CHAIN_ID, fetch=None):
    r = _proxy({"action": "eth_getTransactionCount", "address": _addr(address), "tag": "latest"}, chain_id, fetch)
    return int(r["result"], 16)


def get_gas_fees(*, chain_id=DEFAULT_CHAIN_ID, fetch=None):
    gp = int(_proxy({"action": "eth_gasPrice"}, chain_id, fetch)["result"], 16)
    return {"max_fee_per_gas": gp * 2 or 1, "max_priority_fee_per_gas": min(gp, 2_000_000_000) or 1}


def make_broadcaster(*, chain_id=DEFAULT_CHAIN_ID, fetch=None):
    def broadcast(raw_hex):
        return _proxy({"action": "eth_sendRawTransaction", "hex": raw_hex}, chain_id, fetch).get("result")
    return broadcast


def send_live(wallet, to, value_wei, *, chain="evm", chain_id=DEFAULT_CHAIN_ID, fetch=None):
    """Fetch nonce + gas, sign with the owner's key, and broadcast. Returns the send() result."""
    fees = get_gas_fees(chain_id=chain_id, fetch=fetch)
    return send(
        wallet, to, value_wei, chain=chain,
        nonce=get_nonce(_addr(wallet), chain_id=chain_id, fetch=fetch),
        max_fee_per_gas=fees["max_fee_per_gas"],
        max_priority_fee_per_gas=fees["max_priority_fee_per_gas"],
        chain_id=chain_id, broadcast=make_broadcaster(chain_id=chain_id, fetch=fetch),
    )
