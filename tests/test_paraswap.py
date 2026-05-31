"""Red tests — keyless Paraswap swap with our partner fee (no API key, no registration).

quote_fetch + tx_build + broadcast injected: deterministic, no network/funds. Pins our fee on
the tx-build request and that we sign the returned swap tx with the OWNER's key.
"""
import pytest
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.swap import swap_paraswap, get_paraswap_quote

WPOL = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
USDCE = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
FEE_RECIPIENT = "0x00000000000000000000000000000000FEe0fEE0"
AGG_TO = "0x1111111111111111111111111111111111111111"


def _quote_fetch():
    def fetch(url):
        fetch.url = url
        return {"priceRoute": {"srcToken": WPOL, "destToken": USDCE, "destAmount": "1000000", "srcAmount": "10000000000000000"}}
    fetch.url = None
    return fetch


def _tx_build():
    def build(url, body):
        build.body = body
        return {"to": AGG_TO, "data": "0xabcdef", "value": "0"}
    build.body = None
    return build


def _broadcast():
    def b(raw):
        b.raw = raw
        return "0x" + "ee" * 32
    b.raw = None
    return b


def _do(wallet, qf, tb, bc):
    return swap_paraswap(
        wallet, WPOL, USDCE, 10**16, chain="evm", chain_id=137, fee_recipient=FEE_RECIPIENT,
        nonce=0, max_fee_per_gas=150*10**9, max_priority_fee_per_gas=35*10**9,
        quote_fetch=qf, tx_build=tb, broadcast=bc,
    )


def test_quote_request_hits_paraswap_with_tokens_and_network():
    qf = _quote_fetch()
    _do(create_wallet("evm"), qf, _tx_build(), _broadcast())
    u = qf.url.lower()
    assert WPOL.lower() in u and USDCE.lower() in u, f"tokens missing from quote: {qf.url}"
    assert "network=137" in u, f"network missing: {qf.url}"


def test_tx_build_request_carries_our_partner_fee():
    tb = _tx_build()
    _do(create_wallet("evm"), _quote_fetch(), tb, _broadcast())
    assert tb.body["partnerAddress"].lower() == FEE_RECIPIENT.lower(), f"partner fee recipient missing: {tb.body}"
    assert tb.body["partnerFeeBps"] == 10, f"0.1% fee not attached: {tb.body}"
    assert tb.body["userAddress"], "userAddress (taker) missing"


def test_signed_swap_tx_recovers_to_owner():
    w = create_wallet("evm")
    bc = _broadcast()
    _do(w, _quote_fetch(), _tx_build(), bc)
    assert Account.recover_transaction(bc.raw) == w.address, "swap tx not signed by owner"


def test_result_has_hash_and_no_private_key():
    w = create_wallet("evm")
    res = _do(w, _quote_fetch(), _tx_build(), _broadcast())
    assert res["hash"] == "0x" + "ee" * 32, f"missing network hash: {res}"
    assert res["to"].lower() == AGG_TO.lower()
    assert w.private_key not in str(res), "private key leaked into swap result"


def test_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        swap_paraswap(create_wallet("evm"), WPOL, USDCE, 1, chain="dogecoin", fee_recipient=FEE_RECIPIENT,
                      nonce=0, max_fee_per_gas=1, max_priority_fee_per_gas=1,
                      quote_fetch=_quote_fetch(), tx_build=_tx_build(), broadcast=_broadcast())
