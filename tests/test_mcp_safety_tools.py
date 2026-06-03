"""The MCP surface exposed only wallet ops — our security wedge (preflight + signature inspector)
wasn't reachable by an MCP client at all. These must be first-class MCP tools so any agent runtime
(Claude, etc.) can call the guard before signing.
"""
from chain_signer.mcp_server import list_tools, call_tool, TOOL_NAMES

SPENDER = "0x" + "22" * 20
TOKEN = "0x" + "33" * 20
MAX = (1 << 256) - 1


def test_safety_tools_are_listed():
    assert "preflight" in TOOL_NAMES
    assert "inspect_signature" in TOOL_NAMES


def test_preflight_tool_flags_unlimited_approval():
    tx = {"to": TOKEN, "data": "0x095ea7b3" + SPENDER[2:].rjust(64, "0") + "f" * 64, "value": 0}
    r = call_tool("preflight", {"tx": tx})
    assert r["ok"] is False
    assert any(f["code"] == "unlimited_approval" for f in r["risk_flags"])


def test_inspect_signature_tool_flags_unlimited_permit():
    td = {"primaryType": "Permit",
          "domain": {"verifyingContract": TOKEN},
          "message": {"owner": "0x" + "11" * 20, "spender": SPENDER, "value": str(MAX), "nonce": 0, "deadline": 9999999999}}
    r = call_tool("inspect_signature", {"typed_data": td})
    assert r["ok"] is False
    assert any(f["code"] == "unlimited_permit_signature" for f in r["risk_flags"])


def test_safety_tools_have_schemas():
    specs = {t["name"]: t for t in list_tools()}
    assert "inputSchema" in specs["preflight"]
    assert "inputSchema" in specs["inspect_signature"]
