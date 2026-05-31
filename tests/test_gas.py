"""Red tests — self-funding gas via gasless swap (no upfront native coin).

quote_fetch + submit are injected: deterministic, no network/funds. Pins that our fee is attached,
and that we sign the gasless trade with the OWNER's key (signature recovers to owner).
"""
import pytest
from eth_account import Account
from eth_account.messages import encode_typed_data

from chain_signer import create_wallet
from chain_signer.gas import self_fund_gas

USDCE = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
POL = "0x0000000000000000000000000000000000001010"  # POL on Polygon
FEE_RECIPIENT = "0x00000000000000000000000000000000FEe0fEE0"

# A minimal valid EIP-712 typed message standing in for 0x's gasless `trade.eip712`.
TYPED = {
    "types": {
        "EIP712Domain": [{"name": "name", "type": "string"}, {"name": "chainId", "type": "uint256"}],
        "Trade": [{"name": "taker", "type": "address"}, {"name": "amount", "type": "uint256"}],
    },
    "domain": {"name": "ZeroEx", "chainId": 137},
    "primaryType": "Trade",
    "message": {"taker": "0x000000000000000000000000000000000000dEaD", "amount": 1000000},
}


def _quote_fetch():
    def fetch(url):
        fetch.url = url
        return {"trade": {"eip712": TYPED}}
    fetch.url = None
    return fetch


def _submit():
    def submit(payload):
        submit.payload = payload
        return {"tradeHash": "0x" + "77" * 32}
    submit.payload = None
    return submit


def _do(wallet, quote_fetch, submit):
    return self_fund_gas(
        wallet, USDCE, POL, 2_000_000,  # sell 2 USDC.e for POL
        chain="evm", chain_id=137, fee_recipient=FEE_RECIPIENT,
        quote_fetch=quote_fetch, submit=submit,
    )


def test_quote_request_carries_sell_buy_taker_and_our_fee():
    fetch = _quote_fetch()
    w = create_wallet("evm")
    _do(w, fetch, _submit())
    u = fetch.url.lower()
    assert USDCE.lower() in u and POL.lower() in u, f"sell/buy tokens missing: {fetch.url}"
    assert w.address.lower() in u, "taker (our address) missing from quote request"
    assert "swapfeebps=10" in u, f"0.1% fee not attached: {fetch.url}"


def test_signed_gasless_trade_recovers_to_owner():
    w = create_wallet("evm")
    submit = _submit()
    _do(w, _quote_fetch(), submit)
    sig = submit.payload["signature"]
    recovered = Account.recover_message(encode_typed_data(full_message=TYPED), signature=sig)
    assert recovered == w.address, f"gasless trade signed by {recovered}, not owner {w.address}"


def test_returns_trade_hash_and_no_private_key():
    w = create_wallet("evm")
    res = _do(w, _quote_fetch(), _submit())
    assert res["trade_hash"] == "0x" + "77" * 32, f"missing trade hash: {res}"
    assert w.private_key not in str(res), "private key leaked into gas result"


def test_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        self_fund_gas(create_wallet("evm"), USDCE, POL, 1, chain="dogecoin",
                      fee_recipient=FEE_RECIPIENT, quote_fetch=_quote_fetch(), submit=_submit())
