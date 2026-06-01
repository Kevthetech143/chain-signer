"""Red tests — the tool surface (call_tool) routes all chains: EVM, Solana, Bitcoin."""
import base58
from bit.network.meta import Unspent
from bit.transaction import address_to_scriptpubkey

from chain_signer import create_wallet
from chain_signer.mcp_server import call_tool


def test_create_wallet_solana_and_bitcoin_via_tool():
    s = call_tool("create_wallet", {"chain": "solana"})
    assert len(base58.b58decode(s["address"])) == 32
    b = call_tool("create_wallet", {"chain": "bitcoin"})
    assert b["address"][0] == "1"


def test_get_balance_routes_to_solana():
    bal = call_tool("get_balance", {"chain": "solana", "address": "So11111111111111111111111111111111111111112"},
                    rpc=lambda m, p: {"value": 3_000_000_000})
    assert bal["balance"] == 3.0


def test_get_balance_routes_to_bitcoin_testnet():
    def fetch(url):
        fetch.url = url
        return {"chain_stats": {"funded_txo_sum": 200_000_000, "spent_txo_sum": 0}}
    bal = call_tool("get_balance", {"chain": "bitcoin", "address": "n2goBAxcxVxNQLiNca4zXTH3bKLhardDAV", "testnet": True},
                    fetch=fetch)
    assert bal["balance"] == 2.0 and "testnet" in fetch.url


def test_send_routes_to_solana():
    w = create_wallet("solana")
    bh = base58.b58encode(bytes(32)).decode()
    res = call_tool("send", {"chain": "solana", "private_key": w.private_key,
                             "to": "So11111111111111111111111111111111111111112",
                             "lamports": 1000, "recent_blockhash": bh},
                    broadcast=lambda b64: "SIG" + "1" * 85)
    assert res["from"] == w.address and res["signature"].startswith("SIG")


def test_send_routes_to_bitcoin():
    w = create_wallet("bitcoin", testnet=True)
    u = Unspent(1_000_000, 6, address_to_scriptpubkey(w.address).hex(), "aa" * 32, 0)
    to = create_wallet("bitcoin", testnet=True).address
    res = call_tool("send", {"chain": "bitcoin", "private_key": w.private_key, "testnet": True,
                             "to": to, "amount_btc": 0.001, "unspents": [u]},
                    broadcast=lambda r: "f" * 64)
    assert res["from"] == w.address and res["raw"].startswith("0100000001")
