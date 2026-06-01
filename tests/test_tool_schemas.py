"""Red tests — each tool must advertise a REAL typed input schema, not a catch-all.

Why: MCP directories (Glama et al.) rank servers on tool-schema completeness, and agent
clients need typed params to call our tools correctly. A generic
{"type":"object","additionalProperties":true} is technically valid but low-quality and
gives the calling agent no guidance. These tests pin a real schema per tool: typed
properties + the right required fields, sourced from chain_signer.mcp_server (one source of
truth) and surfaced through the stdio server.
"""
import json

from chain_signer.mcp_server import list_tools
from chain_signer.mcp_stdio import handle


def _by_name():
    return {t["name"]: t for t in list_tools()}


def test_every_tool_advertises_typed_properties_not_catchall():
    for t in list_tools():
        schema = t["inputSchema"]
        assert schema["type"] == "object"
        props = schema.get("properties") or {}
        assert props, f"{t['name']} advertises no typed properties (catch-all only)"


def test_create_wallet_schema_offers_chain_enum():
    schema = _by_name()["create_wallet"]["inputSchema"]
    chain = schema["properties"]["chain"]
    assert set(chain["enum"]) == {"evm", "solana", "bitcoin"}


def test_get_balance_requires_address():
    schema = _by_name()["get_balance"]["inputSchema"]
    assert "address" in schema["required"]


def test_send_requires_key_and_recipient():
    schema = _by_name()["send"]["inputSchema"]
    assert {"private_key", "to"} <= set(schema["required"])


def test_swap_schema_lists_and_requires_token_params():
    schema = _by_name()["swap"]["inputSchema"]
    props = schema["properties"]
    assert {"sell_token", "buy_token", "sell_amount"} <= set(props)
    assert {"sell_token", "buy_token", "sell_amount"} <= set(schema["required"])


def test_bridge_requires_both_chains_and_tokens():
    schema = _by_name()["bridge"]["inputSchema"]
    assert {"from_chain", "to_chain", "from_token", "to_token", "amount"} <= set(schema["required"])


def test_stdio_tools_list_surfaces_the_real_schema():
    r = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    tools = {t["name"]: t for t in r["result"]["tools"]}
    # the stdio surface must carry the SAME typed schema, not the generic catch-all
    assert tools["create_wallet"]["inputSchema"]["properties"]["chain"]["enum"]
