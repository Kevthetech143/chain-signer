"""Tool surface — exposes the chain-signer functions so any AI can call them.

This is the dispatch layer (list_tools / call_tool). An MCP stdio server, an HTTP API, or a
CLI all wrap this same surface — wired at packaging. Non-custodial: signing tools take the
caller's own private_key per call, use it transiently, and never store it.
"""
from .balance import get_balance
from .bitcoin import send_bitcoin
from .bridge import bridge_evm, get_bridge_quote
from .preflight import preflight
from .sig_inspect import inspect_typed_data
from .solana import send_solana
from .swap import swap
from .tx import call_contract, send
from .wallet import create_wallet

# Shared building blocks so every tool advertises consistent, typed params.
_CHAIN = {"type": "string", "enum": ["evm", "solana", "bitcoin"], "default": "evm",
          "description": "Which chain family to act on."}
_KEY = {"type": "string", "description": "The caller's own private key. Used transiently to sign; never stored (non-custodial)."}
# EVM transactions are caller-built: the agent supplies nonce + EIP-1559 gas fields.
_EVM_TX = {
    "nonce": {"type": "integer", "description": "Account nonce for this transaction."},
    "max_fee_per_gas": {"type": "integer", "description": "EIP-1559 max fee per gas (wei)."},
    "max_priority_fee_per_gas": {"type": "integer", "description": "EIP-1559 priority fee per gas (wei)."},
    "gas": {"type": "integer", "description": "Gas limit."},
    "chain_id": {"type": "integer", "default": 137, "description": "EVM chain id (137 = Polygon)."},
}
_EVM_TX_REQUIRED = ["private_key", "nonce", "max_fee_per_gas", "max_priority_fee_per_gas"]


def _schema(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required),
            "additionalProperties": True}


TOOL_SPECS = (
    {"name": "create_wallet",
     "description": "Create or restore a non-custodial wallet; returns the address and the private key (caller keeps the key).",
     "inputSchema": _schema({
         "chain": _CHAIN,
         "private_key": {"type": "string", "description": "Optional: restore an existing wallet from its key; omit to generate a fresh one."},
         "testnet": {"type": "boolean", "default": False, "description": "Use the chain's testnet."},
     })},
    {"name": "get_balance",
     "description": "Read a wallet/address balance from the live chain (read-only).",
     "inputSchema": _schema({
         "address": {"type": "string", "description": "Address to read the balance of."},
         "token": {"type": "string", "description": "Optional token/mint address; omit for the native coin."},
         "chain": _CHAIN,
         "decimals": {"type": "integer", "default": 18, "description": "Token decimals for formatting."},
         "testnet": {"type": "boolean", "default": False},
     }, required=["address"])},
    {"name": "send",
     "description": "Sign and post a native-coin transfer with the caller's own key. EVM one-call: omit nonce/gas and they are auto-fetched + broadcast (or supply them to control the tx). Solana uses lamports; Bitcoin uses amount_btc.",
     "inputSchema": _schema({
         "private_key": _KEY,
         "chain": _CHAIN,
         "to": {"type": "string", "description": "Recipient address."},
         "value_wei": {"type": "integer", "description": "EVM: amount to send in wei."},
         "lamports": {"type": "integer", "description": "Solana: amount to send in lamports."},
         "amount_btc": {"type": "string", "description": "Bitcoin: amount to send in BTC."},
         **_EVM_TX,
     }, required=["private_key", "to"])},
    {"name": "call_contract",
     "description": "Sign and post a call to any contract/app function.",
     "inputSchema": _schema({
         "private_key": _KEY,
         "chain": _CHAIN,
         "contract": {"type": "string", "description": "Target contract address."},
         "function_signature": {"type": "string", "description": "e.g. 'transfer(address,uint256)'."},
         "args": {"type": "array", "description": "Positional arguments for the function.", "items": {}},
         "value": {"type": "integer", "default": 0, "description": "Native value to attach (wei)."},
         **_EVM_TX,
     }, required=["private_key", "contract", "function_signature"] + _EVM_TX_REQUIRED[1:])},
    {"name": "swap",
     "description": "Swap tokens via a DEX aggregator with our built-in fee; non-custodial.",
     "inputSchema": _schema({
         "private_key": _KEY,
         "chain": _CHAIN,
         "sell_token": {"type": "string", "description": "Token address to sell."},
         "buy_token": {"type": "string", "description": "Token address to buy."},
         "sell_amount": {"type": "string", "description": "Amount of sell_token (base units)."},
         "fee_recipient": {"type": "string", "description": "Optional address to receive the integrator fee."},
         **_EVM_TX,
     }, required=["private_key", "sell_token", "buy_token", "sell_amount"] + _EVM_TX_REQUIRED[1:])},
    {"name": "bridge",
     "description": "Move value across chains via LI.FI; signs the route tx with the owner's key.",
     "inputSchema": _schema({
         "private_key": _KEY,
         "from_chain": {"type": "string", "description": "Source chain."},
         "to_chain": {"type": "string", "description": "Destination chain."},
         "from_token": {"type": "string", "description": "Token address on the source chain."},
         "to_token": {"type": "string", "description": "Token address on the destination chain."},
         "amount": {"type": "string", "description": "Amount to bridge (base units)."},
         "integrator": {"type": "string", "default": "chain-signer"},
         **_EVM_TX,
     }, required=["private_key", "from_chain", "to_chain", "from_token", "to_token", "amount"] + _EVM_TX_REQUIRED[1:])},
    # --- Safety wedge: inspect BEFORE signing. Read-only, no key, never sends. ---
    {"name": "preflight",
     "description": "SAFETY: decode an UNSIGNED EVM transaction and flag drain patterns (unlimited/large approval, approve-all, token & NFT transferFrom, proxy upgrade, on-chain permit, approvals hidden in multicall, opaque calldata) BEFORE signing. Returns {decoded, risk_flags, ok}. Read-only; takes no key.",
     "inputSchema": _schema({
         "tx": {"type": "object", "description": "Unsigned tx: {to, data (hex calldata), value}."},
         "max_value": {"type": "integer", "description": "Optional: flag native value above this (wei)."},
     }, required=["tx"])},
    {"name": "inspect_signature",
     "description": "SAFETY: inspect an EIP-712 typed-data message the agent is about to SIGN and flag permit-phishing (ERC-2612, Uniswap Permit2, DAI-style permits granting an unlimited/large allowance). Catches the off-chain drain a transaction check can't see. Returns {decoded, risk_flags, ok}. Read-only; takes no key.",
     "inputSchema": _schema({
         "typed_data": {"type": "object", "description": "EIP-712 typed data: {types, domain, primaryType, message}."},
     }, required=["typed_data"])},
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

    # Safety tools first — read-only, no key, the wedge.
    if name == "preflight":
        return preflight(a.get("tx"), max_value=a.get("max_value"))

    if name == "inspect_signature":
        return inspect_typed_data(a.get("typed_data"))

    if name == "create_wallet":
        w = create_wallet(chain, private_key=a.get("private_key"), testnet=a.get("testnet", False))
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
        # One-call (honors the tool schema: nonce/gas optional): auto-fetch nonce+gas and broadcast.
        if "nonce" not in a:
            from .live import send_live
            return send_live(_wallet(a), a["to"], a["value_wei"], chain=chain,
                             chain_id=a.get("chain_id", 137), fetch=fetch)
        # Explicit path: caller supplied nonce + gas (deterministic, no RPC).
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

    if name == "bridge":
        w = _wallet(a)
        quote = get_bridge_quote(
            a["from_chain"], a["to_chain"], a["from_token"], a["to_token"], a["amount"], w.address,
            integrator=a.get("integrator", "chain-signer"), fee=a.get("fee"), fetch=fetch,
        )
        return bridge_evm(
            w, quote, nonce=a["nonce"], max_fee_per_gas=a["max_fee_per_gas"],
            max_priority_fee_per_gas=a["max_priority_fee_per_gas"], gas=a.get("gas"), broadcast=broadcast,
        )

    raise ValueError(f"unknown tool {name!r}; available: {', '.join(TOOL_NAMES)}")
