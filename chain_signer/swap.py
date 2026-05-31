"""Token swaps via a DEX aggregator (0x), with our tiny built-in integrator fee.

Non-custodial: the user's OWN wallet signs the aggregator-built transaction; the fee is
routed by the aggregator to our collector address — we never hold anyone's funds. The HTTP
and broadcast layers are injectable so logic is unit-testable with no network/funds.

NOTE: exact 0x API param names must be re-confirmed against current docs at the live
fork-proof step; the unit tests here pin OUR behavior (fee attached + we sign the returned tx).
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

from eth_account import Account

from .fee import DEFAULT_FEE_BPS
from .tx import _addr, _to_0x_hex

SUPPORTED_CHAINS = ("evm",)
CHAIN_IDS = {"evm": 137}
ZEROX_QUOTE_URL = "https://api.0x.org/swap/permit2/quote"
PARASWAP_PRICES_URL = "https://api.paraswap.io/prices"
PARASWAP_TX_URL = "https://api.paraswap.io/transactions"


def _default_fetch(url: str) -> dict:
    with urlopen(url, timeout=20) as resp:  # noqa: S310
        return json.load(resp)


def get_swap_quote(sell_token, buy_token, sell_amount, taker, *, chain="evm", fee_recipient, fee_bps=DEFAULT_FEE_BPS, fetch=None):
    """Request a swap quote with OUR integrator fee attached. Returns the aggregator quote."""
    if chain not in SUPPORTED_CHAINS:
        raise ValueError(f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}")
    fetch = fetch or _default_fetch
    params = {
        "chainId": CHAIN_IDS[chain],
        "sellToken": sell_token,
        "buyToken": buy_token,
        "sellAmount": int(sell_amount),
        "taker": taker,
        "swapFeeRecipient": fee_recipient,  # our collector
        "swapFeeBps": int(fee_bps),         # 0.1%
        "swapFeeToken": buy_token,
    }
    return fetch(ZEROX_QUOTE_URL + "?" + urlencode(params))


def swap(wallet, sell_token, buy_token, sell_amount, *, chain="evm", fee_recipient=None, fee_bps=DEFAULT_FEE_BPS, nonce, max_fee_per_gas, max_priority_fee_per_gas, gas=300000, chain_id=137, fetch=None, broadcast=None):
    """Get a fee-bearing quote, then sign + post the aggregator's transaction with the owner's key."""
    if chain not in SUPPORTED_CHAINS:
        raise ValueError(f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}")
    fee_recipient = fee_recipient or os.environ.get("CHAIN_SIGNER_FEE_RECIPIENT", "")
    quote = get_swap_quote(
        sell_token, buy_token, sell_amount, _addr(wallet),
        chain=chain, fee_recipient=fee_recipient, fee_bps=fee_bps, fetch=fetch,
    )
    t = quote["transaction"]
    tx = {
        "to": t["to"],
        "data": t.get("data", "0x"),
        "value": int(t.get("value", 0) or 0),
        "nonce": int(nonce),
        "gas": int(gas),
        "maxFeePerGas": int(max_fee_per_gas),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas),
        "chainId": int(chain_id),
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
        "hash": tx_hash,
        "from": _addr(wallet),
        "to": t["to"],
        "sell": sell_token,
        "buy": buy_token,
        "fee_bps": int(fee_bps),
        "fee_recipient": fee_recipient,
        "raw": raw_hex,
    }


def _default_tx_build(url: str, body: dict) -> dict:
    from urllib.request import Request
    req = Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=20) as resp:  # noqa: S310
        return json.load(resp)


def get_paraswap_quote(sell_token, buy_token, sell_amount, *, src_decimals=18, dest_decimals=6, chain_id=137, fetch=None):
    """Keyless Paraswap price quote. Returns the response containing priceRoute."""
    params = {
        "srcToken": sell_token, "destToken": buy_token, "amount": int(sell_amount),
        "srcDecimals": int(src_decimals), "destDecimals": int(dest_decimals),
        "side": "SELL", "network": int(chain_id),
    }
    return (fetch or _default_fetch)(PARASWAP_PRICES_URL + "/?" + urlencode(params))


def swap_paraswap(wallet, sell_token, buy_token, sell_amount, *, src_decimals=18, dest_decimals=6,
                  chain="evm", chain_id=137, fee_recipient=None, fee_bps=DEFAULT_FEE_BPS, slippage_bps=100,
                  nonce, max_fee_per_gas, max_priority_fee_per_gas, gas=400000,
                  quote_fetch=None, tx_build=None, broadcast=None):
    """Keyless swap via Paraswap with our partner fee; sign + broadcast with the owner's key."""
    if chain not in SUPPORTED_CHAINS:
        raise ValueError(f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}")
    fee_recipient = fee_recipient or os.environ.get("CHAIN_SIGNER_FEE_RECIPIENT", "")
    route = get_paraswap_quote(sell_token, buy_token, sell_amount, src_decimals=src_decimals,
                               dest_decimals=dest_decimals, chain_id=chain_id, fetch=quote_fetch)["priceRoute"]
    min_dest = int(route["destAmount"]) * (10_000 - int(slippage_bps)) // 10_000
    body = {
        "srcToken": sell_token, "destToken": buy_token,
        "srcAmount": str(int(sell_amount)), "destAmount": str(min_dest),
        "priceRoute": route, "userAddress": _addr(wallet),
        "partner": "chain-signer", "partnerAddress": fee_recipient, "partnerFeeBps": int(fee_bps),
        "srcDecimals": int(src_decimals), "destDecimals": int(dest_decimals),
    }
    tx = (tx_build or _default_tx_build)(f"{PARASWAP_TX_URL}/{int(chain_id)}", body)
    full = {
        "to": tx["to"], "data": tx.get("data", "0x"), "value": int(tx.get("value", 0) or 0),
        "nonce": int(nonce), "gas": int(gas), "maxFeePerGas": int(max_fee_per_gas),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas), "chainId": int(chain_id), "type": 2,
    }
    signed = Account.sign_transaction(full, wallet.private_key)
    raw_hex = _to_0x_hex(getattr(signed, "raw_transaction", None) or signed.rawTransaction)
    tx_hash = _to_0x_hex(getattr(signed, "hash", None) or signed.hash)
    if broadcast is not None:
        returned = broadcast(raw_hex)
        if returned:
            tx_hash = returned
    return {
        "hash": tx_hash, "from": _addr(wallet), "to": tx["to"],
        "sell": sell_token, "buy": buy_token, "fee_bps": int(fee_bps), "fee_recipient": fee_recipient,
        "min_received": min_dest, "raw": raw_hex,
    }
