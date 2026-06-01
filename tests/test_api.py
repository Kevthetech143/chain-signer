"""Red tests — the V1 developer-facing facade: think in ETH, send in one call.

No network/funds: the live RPC is injected via `fetch`. Pins (1) exact ether->wei
conversion and (2) that send_ether wires nonce/gas/broadcast and is signed by the owner.
"""
from eth_account import Account

from chain_signer import create_wallet, to_wei, send_ether

TO = "0x000000000000000000000000000000000000dEaD"


def _rpc_fetch():
    def fetch(url):
        fetch.calls.append(url)
        if "eth_getTransactionCount" in url:
            return {"result": "0x5"}
        if "eth_gasPrice" in url:
            return {"result": hex(30_000_000_000)}
        if "eth_sendRawTransaction" in url:
            return {"result": "0x" + "99" * 32}
        return {"result": "0x0"}
    fetch.calls = []
    return fetch


def test_to_wei_converts_whole_ether_to_integer_wei():
    assert to_wei(1) == 10**18


def test_to_wei_handles_fractional_ether_exactly():
    assert to_wei(0.001) == 10**15
    assert to_wei("0.5") == 5 * 10**17


def test_to_wei_returns_int_not_float():
    assert isinstance(to_wei(0.001), int)


def test_send_ether_broadcasts_and_is_signed_by_owner():
    w = create_wallet("evm")
    fetch = _rpc_fetch()
    res = send_ether(w, TO, 0.001, chain_id=80002, fetch=fetch)
    assert res["hash"] == "0x" + "99" * 32, f"did not return network hash: {res.get('hash')}"
    assert Account.recover_transaction(res["raw"]) == w.address, "send_ether not signed by owner"
    assert any("eth_sendRawTransaction" in u for u in fetch.calls), "never broadcast the raw tx"
