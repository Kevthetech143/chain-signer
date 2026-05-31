"""Red tests — read on-chain balance from the live chain (read-only).

The HTTP layer is injected (`fetch`) so logic is deterministic with no network/funds.
Tests pin BEHAVIOR: decimal conversion + that we query the right endpoint.
"""
import pytest

from chain_signer import create_wallet
from chain_signer.balance import get_balance


def _fake_fetch(result):
    """Return a fetch() that records the URL it was called with and returns canned JSON."""
    def fetch(url):
        fetch.url = url
        return {"status": "1", "result": result}
    fetch.url = None
    return fetch


def test_native_balance_converts_from_wei_to_whole_coins():
    fetch = _fake_fetch("9854633000000000000")  # 9.854633 POL in wei
    bal = get_balance("0x01F5404f0FFCEFBA097817cC3765556240db46aD", fetch=fetch)
    assert bal == pytest.approx(9.854633), f"wei not converted by 1e18: got {bal}"


def test_token_balance_converts_by_decimals_and_queries_token_endpoint():
    fetch = _fake_fetch("66221179")  # 66.221179 USDC (6 decimals)
    token = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
    bal = get_balance("0x01F5404f0FFCEFBA097817cC3765556240db46aD", token=token, decimals=6, fetch=fetch)
    assert bal == pytest.approx(66.221179), f"token not converted by 1e6: got {bal}"
    assert token.lower() in fetch.url.lower(), f"token contract missing from query: {fetch.url}"
    assert "tokenbalance" in fetch.url, f"did not use tokenbalance action: {fetch.url}"
    assert "chainid=137" in fetch.url, f"did not target Polygon chainid=137: {fetch.url}"


def test_accepts_a_wallet_object_and_uses_its_address():
    w = create_wallet("evm")
    fetch = _fake_fetch("0")
    bal = get_balance(w, fetch=fetch)
    assert bal == 0, f"expected 0 balance, got {bal}"
    assert w.address.lower() in fetch.url.lower(), f"wallet address missing from query: {fetch.url}"


def test_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        get_balance("0x01F5404f0FFCEFBA097817cC3765556240db46aD", chain="dogecoin", fetch=_fake_fetch("0"))
