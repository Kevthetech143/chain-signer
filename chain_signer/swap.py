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
