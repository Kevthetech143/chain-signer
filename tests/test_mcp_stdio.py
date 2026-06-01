"""Red tests — real MCP stdio server (JSON-RPC 2.0) wrapping our tool dispatch.

Verifies the handshake + tools/list + tools/call so a registry listing claiming a stdio
MCP server is TRUE, not aspirational. Pure handler tested (no process needed).
"""
import json
from chain_signer.mcp_stdio import handle


def test_initialize_returns_protocol_and_server_info():
    r = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"}})
    assert r["id"] == 1
    assert r["result"]["serverInfo"]["name"]
    assert "capabilities" in r["result"]
    assert r["result"]["protocolVersion"]


def test_initialized_notification_yields_no_response():
    assert handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_tools_list_exposes_six_tools_with_input_schema():
    r = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = r["result"]["tools"]
    assert len(tools) == 6
    names = {t["name"] for t in tools}
    assert {"create_wallet", "send", "swap"} <= names
    assert all("inputSchema" in t for t in tools), "every tool must advertise an inputSchema"


def test_tools_call_create_wallet_returns_content():
    r = handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "create_wallet", "arguments": {"chain": "evm"}}})
    content = r["result"]["content"]
    assert content and content[0]["type"] == "text"
    payload = json.loads(content[0]["text"])
    assert payload["address"].startswith("0x")


def test_unknown_method_returns_jsonrpc_error():
    r = handle({"jsonrpc": "2.0", "id": 9, "method": "no/such"})
    assert r["error"]["code"] == -32601
