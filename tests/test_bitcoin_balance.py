"""Red tests — Bitcoin balance via chain dispatch (keyless Blockstream API), mainnet + testnet."""
import pytest

from chain_signer.balance import get_balance


def test_bitcoin_balance_converts_sats_to_btc():
    def fetch(url):
        fetch.url = url
        return {"chain_stats": {"funded_txo_sum": 150_000_000, "spent_txo_sum": 50_000_000}}
    bal = get_balance("1KLs663o8LEkhRx41zbdc1EUHXrznBTKSs", chain="bitcoin", fetch=fetch)
    assert bal == pytest.approx(1.0), f"sats not converted (funded-spent)/1e8: {bal}"
    assert "/address/1KLs663o8LEkhRx41zbdc1EUHXrznBTKSs" in fetch.url


def test_bitcoin_testnet_uses_testnet_endpoint():
    def fetch(url):
        fetch.url = url
        return {"chain_stats": {"funded_txo_sum": 0, "spent_txo_sum": 0}}
    bal = get_balance("n2goBAxcxVxNQLiNca4zXTH3bKLhardDAV", chain="bitcoin", testnet=True, fetch=fetch)
    assert bal == 0
    assert "testnet" in fetch.url, f"did not hit the testnet endpoint: {fetch.url}"


def test_solana_balance_still_works():
    bal = get_balance("So11111111111111111111111111111111111111112", chain="solana", rpc=lambda m, p: {"value": 2_000_000_000})
    assert bal == pytest.approx(2.0)
