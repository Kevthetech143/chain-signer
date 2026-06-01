"""Cross-chain bridging via LI.FI.

Get a route quote, then sign the LI.FI-returned EVM transaction with the owner's key and broadcast it —
non-custodial, reusing the sign-and-broadcast pattern. LI.FI is behind Cloudflare: the default Python
user-agent gets a 403 (error 1010), so the default fetch sends a browser User-Agent. GREEN STEP fills this in.
"""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from eth_account import Account

from .tx import _addr, _to_0x_hex

LIFI_QUOTE_URL = "https://li.quest/v1/quote"
_BROWSER_UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


def _default_lifi_fetch(url: str) -> dict:
    with urlopen(Request(url, headers=_BROWSER_UA), timeout=25) as resp:  # noqa: S310
        return json.load(resp)


def _to_int(x) -> int:
    if isinstance(x, str):
        return int(x, 16) if x.lower().startswith("0x") else int(x)
    return int(x)


def get_bridge_quote(from_chain, to_chain, from_token, to_token, amount, from_address, *, integrator="chain-signer", fee=None, fetch=None):
    """Get a cross-chain route from LI.FI. Returns the quote (incl. transactionRequest)."""
    params = {
        "fromChain": from_chain, "toChain": to_chain,
        "fromToken": from_token, "toToken": to_token,
        "fromAmount": int(amount), "fromAddress": _addr(from_address),
        "integrator": integrator,
    }
    if fee is not None:
        params["fee"] = fee
    return (fetch or _default_lifi_fetch)(LIFI_QUOTE_URL + "?" + urlencode(params))


def bridge_evm(wallet, quote, *, nonce, max_fee_per_gas, max_priority_fee_per_gas, gas=None, broadcast=None):
    """Sign the LI.FI transactionRequest with the owner's EVM key and broadcast. Returns the tx hash."""
    tr = quote["transactionRequest"]
    tx = {
        "to": tr["to"],
        "data": tr.get("data", "0x"),
        "value": _to_int(tr.get("value", 0)),
        "nonce": int(nonce),
        "gas": int(gas) if gas is not None else _to_int(tr.get("gasLimit", 500000)),
        "maxFeePerGas": int(max_fee_per_gas),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas),
        "chainId": _to_int(tr["chainId"]),
        "type": 2,
    }
    signed = Account.sign_transaction(tx, wallet.private_key)
    raw_hex = _to_0x_hex(getattr(signed, "raw_transaction", None) or signed.rawTransaction)
    tx_hash = _to_0x_hex(getattr(signed, "hash", None) or signed.hash)
    if broadcast is not None:
        returned = broadcast(raw_hex)
        if returned:
            tx_hash = returned
    return {
        "hash": tx_hash, "from": _addr(wallet), "to": tr["to"],
        "tool": quote.get("tool"), "est_received": quote.get("estimate", {}).get("toAmount"),
        "raw": raw_hex,
    }
