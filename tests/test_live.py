"""Red tests — the live adapter (fetch nonce + gas, broadcast). RPC injected: no network/funds."""
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.live import get_nonce, get_gas_fees, make_broadcaster, send_live

TO = "0x000000000000000000000000000000000000dEaD"


def _rpc_fetch():
    def fetch(url):
        fetch.calls.append(url)
        if "eth_getTransactionCount" in url:
            return {"result": "0x5"}
        if "eth_gasPrice" in url:
            return {"result": hex(30_000_000_000)}
        if "eth_sendRawTransaction" in url:
            fetch.sent = url
            return {"result": "0x" + "99" * 32}
        return {"result": "0x0"}
    fetch.calls = []
    fetch.sent = None
    return fetch


def test_get_nonce_parses_hex_to_int():
    assert get_nonce("0x000000000000000000000000000000000000dEaD", fetch=_rpc_fetch()) == 5


def test_get_gas_fees_derived_from_gas_price():
    fees = get_gas_fees(fetch=_rpc_fetch())
    assert fees["max_fee_per_gas"] == 60_000_000_000, f"maxFee wrong: {fees}"
    assert fees["max_priority_fee_per_gas"] <= fees["max_fee_per_gas"]


def test_broadcaster_posts_raw_and_returns_network_hash():
    broadcast = make_broadcaster(fetch=_rpc_fetch())
    assert broadcast("0xdeadbeef") == "0x" + "99" * 32


def test_send_live_wires_nonce_gas_broadcast_and_recovers_to_owner():
    w = create_wallet("evm")
    fetch = _rpc_fetch()
    res = send_live(w, TO, 1000, chain_id=80002, fetch=fetch)
    assert res["hash"] == "0x" + "99" * 32, f"did not return network hash: {res.get('hash')}"
    assert Account.recover_transaction(res["raw"]) == w.address, "live send not signed by owner"
    assert any("eth_sendRawTransaction" in u for u in fetch.calls), "never broadcast the raw tx"
