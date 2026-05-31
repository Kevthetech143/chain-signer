"""Self-funding gas — convert a little stablecoin into POL with NO upfront gas (gasless).

Uses the 0x Gasless API: request a quote, sign the returned EIP-712 trade with the owner's key,
submit the signed trade; the relayer pays the network fee and takes it from the sold token. This
is what lets the tool fund its own gas with no human. HTTP is injected for tests (no funds).
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from eth_account import Account
from eth_account.messages import encode_typed_data

from .fee import DEFAULT_FEE_BPS
from .tx import _addr, _to_0x_hex

SUPPORTED_CHAINS = ("evm",)
GASLESS_QUOTE_URL = "https://api.0x.org/gasless/quote"
GASLESS_SUBMIT_URL = "https://api.0x.org/gasless/submit"


def _default_quote_fetch(url: str) -> dict:
    req = Request(url, headers={"0x-version": "v2", "0x-api-key": os.environ.get("ZEROX_API_KEY", "")})
    with urlopen(req, timeout=20) as resp:  # noqa: S310
        return json.load(resp)


def _default_submit(payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = Request(GASLESS_SUBMIT_URL, data=data,
                  headers={"0x-version": "v2", "0x-api-key": os.environ.get("ZEROX_API_KEY", ""),
                           "Content-Type": "application/json"})
    with urlopen(req, timeout=20) as resp:  # noqa: S310
        return json.load(resp)


def _sign_eip712(typed_data: dict, private_key: str) -> str:
    signed = Account.sign_message(encode_typed_data(full_message=typed_data), private_key)
    return _to_0x_hex(signed.signature)


def self_fund_gas(wallet, sell_token, buy_token, sell_amount, *, chain="evm", chain_id=137,
                  fee_recipient=None, fee_bps=DEFAULT_FEE_BPS, quote_fetch=None, submit=None):
    """Gaslessly sell `sell_token` for `buy_token` (e.g. USDC.e -> POL). Returns the trade hash."""
    if chain not in SUPPORTED_CHAINS:
        raise ValueError(f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}")
    fee_recipient = fee_recipient or os.environ.get("CHAIN_SIGNER_FEE_RECIPIENT", "")
    params = {
        "chainId": int(chain_id),
        "sellToken": sell_token,
        "buyToken": buy_token,
        "sellAmount": int(sell_amount),
        "taker": _addr(wallet),
        "swapFeeRecipient": fee_recipient,
        "swapFeeBps": int(fee_bps),
        "swapFeeToken": buy_token,
    }
    quote = (quote_fetch or _default_quote_fetch)(GASLESS_QUOTE_URL + "?" + urlencode(params))
    typed = quote["trade"]["eip712"]
    signature = _sign_eip712(typed, wallet.private_key)
    payload = {"trade": quote["trade"], "signature": signature, "chainId": int(chain_id)}
    result = (submit or _default_submit)(payload)
    return {
        "trade_hash": result.get("tradeHash"),
        "from": _addr(wallet),
        "sold": sell_token,
        "bought": buy_token,
    }
