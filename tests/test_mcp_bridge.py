"""Red tests — the tool surface exposes and routes "bridge" (cross-chain via LI.FI)."""
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.mcp_server import call_tool, list_tools

LIFI_DIAMOND = "0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE"
QUOTE = {
    "tool": "across", "estimate": {"toAmount": "991195"},
    "transactionRequest": {"to": LIFI_DIAMOND, "data": "0xabcdef", "value": "0x0", "chainId": "0x89", "gasLimit": "0x7a120"},
}


def test_bridge_is_in_the_tool_list():
    assert "bridge" in {t["name"] for t in list_tools()}


def test_call_tool_bridge_routes_quotes_and_signs_to_owner():
    w = create_wallet("evm")
    cap = {}
    def bc(raw):
        cap["raw"] = raw
        return "0x" + "cc" * 32
    res = call_tool("bridge", {
        "private_key": w.private_key, "from_chain": 137, "to_chain": 42161,
        "from_token": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        "to_token": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "amount": 1_000_000, "nonce": 0,
        "max_fee_per_gas": 150 * 10**9, "max_priority_fee_per_gas": 35 * 10**9,
    }, fetch=lambda url: QUOTE, broadcast=bc)
    assert res["hash"] == "0x" + "cc" * 32
    assert Account.recover_transaction(cap["raw"]) == w.address
    assert res["to"].lower() == LIFI_DIAMOND.lower()
