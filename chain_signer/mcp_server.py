"""Tool surface — exposes the chain-signer functions so any AI can call them.

This is the dispatch layer (list_tools / call_tool). An MCP stdio server, an HTTP API, or a
CLI all wrap this same surface — wired at packaging. Non-custodial: signing tools take the
caller's own private_key per call, use it transiently, and never store it.
"""
from .balance import get_balance
from .bitcoin import send_bitcoin
from .solana import send_solana
from .swap import swap
from .tx import call_contract, send
from .wallet import create_wallet

TOOL_SPECS = (
    {"name": "create_wallet", "description": "Create or restore a non-custodial wallet; returns the address and the private key (caller keeps the key)."},
    {"name": "get_balance", "description": "Read a wallet/address balance from the live chain (read-only)."},
    {"name": "send", "description": "Sign and post a native-coin transfer with the caller's own key."},
    {"name": "call_contract", "description": "Sign and post a call to any contract/app function."},
    {"name": "swap", "description": "Swap tokens via a DEX aggregator with our built-in fee; non-custodial."},
)
TOOL_NAMES = tuple(t["name"] for t in TOOL_SPECS)


def list_tools():
    """Return the available tool specs (name + description)."""
    return [dict(t) for t in TOOL_SPECS]


def _wallet(args):
    return create_wallet(args.get("chain", "evm"), private_key=args.get("private_key"),
                         testnet=args.get("testnet", False))


def call_tool(name, arguments, *, fetch=None, broadcast=None, rpc=None):
    """Dispatch a tool call by name to the underlying function. Returns a JSON-able dict."""
    a = dict(arguments or {})
    chain = a.get("chain", "evm")

    if name == "create_wallet":
        w = create_wallet(chain, testnet=a.get("testnet", False))
        return {"address": w.address, "private_key": w.private_key}

    if name == "get_balance":
        bal = get_balance(
            a["address"], token=a.get("token"), chain=chain,
            decimals=a.get("decimals", 18), fetch=fetch, rpc=rpc, testnet=a.get("testnet", False),
        )
        return {"balance": bal}

    if name == "send":
        if chain == "solana":
            return send_solana(_wallet(a), a["to"], a["lamports"],
                               recent_blockhash=a.get("recent_blockhash"), rpc=rpc, broadcast=broadcast)
        if chain == "bitcoin":
            return send_bitcoin(_wallet(a), a["to"], a["amount_btc"],
                                unspents=a.get("unspents"), fee=a.get("fee"), broadcast=broadcast)
        return send(
            _wallet(a), a["to"], a["value_wei"], chain=chain,
            nonce=a["nonce"], max_fee_per_gas=a["max_fee_per_gas"],
            max_priority_fee_per_gas=a["max_priority_fee_per_gas"],
            gas=a.get("gas", 21000), chain_id=a.get("chain_id", 137), broadcast=broadcast,
        )

    if name == "call_contract":
        return call_contract(
            _wallet(a), a["contract"], a["function_signature"], a.get("args", ()),
            value=a.get("value", 0), chain=chain,
            nonce=a["nonce"], max_fee_per_gas=a["max_fee_per_gas"],
            max_priority_fee_per_gas=a["max_priority_fee_per_gas"],
            gas=a.get("gas", 120000), chain_id=a.get("chain_id", 137), broadcast=broadcast,
        )

    if name == "swap":
        return swap(
            _wallet(a), a["sell_token"], a["buy_token"], a["sell_amount"], chain=chain,
            fee_recipient=a.get("fee_recipient"),
            nonce=a["nonce"], max_fee_per_gas=a["max_fee_per_gas"],
            max_priority_fee_per_gas=a["max_priority_fee_per_gas"],
            gas=a.get("gas", 300000), chain_id=a.get("chain_id", 137),
            fetch=fetch, broadcast=broadcast,
        )

    raise ValueError(f"unknown tool {name!r}; available: {', '.join(TOOL_NAMES)}")
