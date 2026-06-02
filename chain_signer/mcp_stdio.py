"""Real MCP stdio server — newline-delimited JSON-RPC 2.0 over stdin/stdout.

Wraps the tool dispatch (mcp_server.list_tools / call_tool) so chain-signer is an actual
MCP server an agent client can connect to. Zero extra deps. Run: `chain-signer-mcp`
(or `python -m chain_signer.mcp_stdio`).
"""
import json
import sys

from importlib.metadata import version, PackageNotFoundError
from .mcp_server import list_tools, call_tool

PROTOCOL_VERSION = "2024-11-05"


def _version():
    try:
        return version("chain-signer")
    except PackageNotFoundError:
        return "0.0.0"


def _tools_for_mcp():
    # Surface the real typed inputSchema from the shared tool surface (one source of truth).
    # Fall back to a permissive object only if a spec somehow lacks one.
    out = []
    for t in list_tools():
        out.append({
            "name": t["name"],
            "description": t.get("description", ""),
            "inputSchema": t.get("inputSchema") or {"type": "object", "additionalProperties": True},
        })
    return out


def handle(msg):
    """Handle one JSON-RPC message. Returns a response dict, or None for notifications."""
    method = msg.get("method")
    msg_id = msg.get("id")

    # JSON-RPC: a request with no `id` member is a NOTIFICATION and MUST get no response —
    # for ANY method, not just notifications/*. (id: 0 is a real id and is handled below.)
    if "id" not in msg:
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}

    if method == "initialize":
        client_pv = (msg.get("params") or {}).get("protocolVersion") or PROTOCOL_VERSION
        return ok({
            "protocolVersion": client_pv,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "chain-signer", "version": _version()},
        })
    if method == "tools/list":
        return ok({"tools": _tools_for_mcp()})
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = call_tool(name, arguments)
            text = result if isinstance(result, str) else json.dumps(result, default=str)
            return ok({"content": [{"type": "text", "text": text}], "isError": False})
        except Exception as e:  # surface tool errors as MCP tool errors, not transport crashes
            # Defensive scrub: never let a secret the caller passed echo back through an error string.
            text = f"error: {e}"
            secret = arguments.get("private_key") if isinstance(arguments, dict) else None
            if secret and secret in text:
                text = "error: tool call failed (details withheld to avoid leaking the private key)"
            return ok({"content": [{"type": "text", "text": text}], "isError": True})
    if method == "ping":
        return ok({})
    if msg_id is None:
        return None  # unknown notification
    return err(-32601, f"method not found: {method}")


def main(argv=None):
    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            out.write(json.dumps(resp) + "\n")
            out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
