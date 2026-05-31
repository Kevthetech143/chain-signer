"""Red tests — token swap with our tiny built-in fee (non-custodial).

HTTP (`fetch`) and `broadcast` are injected: deterministic, no network/funds. Pins that our
fee recipient + 0.1% are attached to the quote request, and that we sign the aggregator's
returned tx with the owner's own key (recovers to owner).
"""
import pytest
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.swap import swap, get_swap_quote
from chain_signer.fee import DEFAULT_FEE_BPS, fee_fraction

SELL = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC.e
BUY = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"   # WMATIC
FEE_RECIPIENT = "0x00000000000000000000000000000000FEe0fEE0"  # our collector (sample)
AGGREGATOR_TX_TO = "0x1111111111111111111111111111111111111111"


def _quote_fetch():
    def fetch(url):
        fetch.url = url
        return {"transaction": {"to": AGGREGATOR_TX_TO, "data": "0xabcdef", "value": "0"}}
    fetch.url = None
    return fetch


def _broadcast():
    def b(raw):
        b.raw = raw
        b.calls += 1
        return "0x" + "ef" * 32
    b.raw = None
    b.calls = 0
    return b


def _do_swap(wallet, fetch, broadcast):
    return swap(
        wallet, SELL, BUY, 1_000_000,
        chain="evm", fee_recipient=FEE_RECIPIENT,
        nonce=0, max_fee_per_gas=30_000_000_000, max_priority_fee_per_gas=1_000_000_000,
        chain_id=137, fetch=fetch, broadcast=broadcast,
    )


def test_default_fee_is_one_tenth_of_one_percent():
    assert DEFAULT_FEE_BPS == 10, "fee should be 10 bps (0.1%)"
    assert fee_fraction() == pytest.approx(0.001), f"fee fraction wrong: {fee_fraction()}"


def test_quote_request_carries_our_fee_recipient_and_bps():
    fetch = _quote_fetch()
    _do_swap(create_wallet("evm"), fetch, _broadcast())
    assert FEE_RECIPIENT.lower() in fetch.url.lower(), f"fee recipient not in quote request: {fetch.url}"
    assert "swapfeebps=10" in fetch.url.lower(), f"0.1% fee not attached to quote: {fetch.url}"


def test_swap_signs_the_aggregator_tx_and_recovers_to_owner():
    w = create_wallet("evm")
    broadcast = _broadcast()
    _do_swap(w, _quote_fetch(), broadcast)
    sender = Account.recover_transaction(broadcast.raw)
    assert sender == w.address, f"swap tx recovered to {sender}, not owner {w.address}"


def test_swap_posts_the_aggregator_transaction_target():
    res = _do_swap(create_wallet("evm"), _quote_fetch(), _broadcast())
    assert res["to"].lower() == AGGREGATOR_TX_TO.lower(), f"wrong tx target: {res['to']}"


def test_swap_result_never_contains_the_private_key():
    w = create_wallet("evm")
    res = _do_swap(w, _quote_fetch(), _broadcast())
    assert w.private_key not in str(res), "private key leaked into swap result"


def test_swap_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        swap(
            create_wallet("evm"), SELL, BUY, 1,
            chain="dogecoin", fee_recipient=FEE_RECIPIENT,
            nonce=0, max_fee_per_gas=1, max_priority_fee_per_gas=1, chain_id=1,
            fetch=_quote_fetch(), broadcast=_broadcast(),
        )
