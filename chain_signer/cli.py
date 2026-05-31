"""Runnable entry point: a thin CLI wrapping the tool surface.

  python -m chain_signer list
  python -m chain_signer call <tool> '<json-args>'

Same surface an MCP server would expose.
"""
import json
import sys

from .mcp_server import call_tool, list_tools

USAGE = "usage: chain_signer [list | call <tool> '<json-args>']"


def main(argv=None):
    """Run the CLI. Returns an exit code (0 ok, non-zero on error)."""
    argv = list(sys.argv[1:]) if argv is None else list(argv)
    if not argv:
        print(USAGE)
        return 2

    cmd = argv[0]
    if cmd == "list":
        print(json.dumps(list_tools(), indent=2))
        return 0

    if cmd == "call":
        if len(argv) < 2:
            print(USAGE)
            return 2
        tool = argv[1]
        arguments = json.loads(argv[2]) if len(argv) > 2 else {}
        result = call_tool(tool, arguments)
        print(json.dumps(result))
        return 0

    print(f"unknown command {cmd!r}\n{USAGE}")
    return 2
