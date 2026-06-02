"""Red test — the MCP `send` tool must honor its own schema: nonce/gas are OPTIONAL.

The send tool's inputSchema marks only private_key + to as required, advertising a true one-call
send. But the dispatch hard-required a["nonce"]/a["max_fee_per_gas"], so an agent calling it the
one-call way (key + to + amount, no nonce/gas) crashed with KeyError. This pins the fix: when nonce
is omitted, the tool auto-fetches nonce+gas and broadcasts (via the live adapter), RPC injected.
"""
from eth_account import Account

from chain_signer.mcp_server import call_tool

TO = "0x000000000000000000000000000000000000dEaD"


def _rpc_fetch():
    def fetch(url):
        fetch.calls.append(url)
        if "eth_getTransactionCount" in url:
            return {"result": "0x7"}
        if "eth_gasPrice" in url:
            return {"result": hex(30_000_000_000)}
        if "eth_sendRawTransaction" in url:
            return {"result": "0x" + "ab" * 32}
        return {"result": "0x0"}
    fetch.calls = []
    return fetch


def test_send_tool_is_one_call_when_nonce_gas_omitted():
    w = call_tool("create_wallet", {"chain": "evm"})
    fetch = _rpc_fetch()
    # one-call: no nonce, no gas — exactly what the schema says is allowed
    res = call_tool("send", {
        "chain": "evm", "private_key": w["private_key"], "to": TO,
        "value_wei": 1000, "chain_id": 80002,
    }, fetch=fetch)
    assert res["hash"] == "0x" + "ab" * 32, f"did not broadcast/return network hash: {res.get('hash')}"
    assert Account.recover_transaction(res["raw"]) == w["address"], "not signed by the owner"
    assert any("eth_getTransactionCount" in u for u in fetch.calls), "nonce was not auto-fetched"
    assert any("eth_sendRawTransaction" in u for u in fetch.calls), "tx was not broadcast"
