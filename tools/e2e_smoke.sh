#!/usr/bin/env bash
# End-to-end smoke test of the PUBLISHED chain-signer — exactly what a new user gets from PyPI.
# Installs the live package in a throwaway venv (no repo code on path), then exercises the real
# product: offline wallet+sign+recover+encrypt roundtrip AND the chain-signer-mcp stdio handshake.
# Exit 0 = PASS, non-zero = FAIL. Prints a plain report. No funds, no network sends, no key risk.
set -u
VENV="$(mktemp -d)/v"
PKG="chain-signer"
fail() { echo "E2E FAIL: $1"; exit 1; }

echo "== chain-signer E2E smoke (live PyPI) =="
python3 -m venv "$VENV" || fail "venv create"
"$VENV/bin/pip" install -q --no-cache-dir "$PKG" || fail "pip install from PyPI"

# 1) installed version == latest on PyPI (caught nothing-shipped / wrong-version regressions)
INST=$("$VENV/bin/python" -c "from importlib.metadata import version; print(version('chain-signer'))") || fail "import metadata"
LATEST=$("$VENV/bin/python" -c "import urllib.request,json; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/chain-signer/json'))['info']['version'])") || fail "pypi query"
echo "installed=$INST  pypi_latest=$LATEST"
[ "$INST" = "$LATEST" ] || echo "  WARN: installed != latest (CDN lag possible)"

# 2) offline product flow against the INSTALLED package (not repo code)
"$VENV/bin/python" - <<'PY' || fail "offline product flow"
from chain_signer import burner, sign_message, export_encrypted, load_encrypted
from eth_account import Account
from eth_account.messages import encode_defunct
w = burner()
assert w.address.startswith("0x") and len(w.address) == 42, "bad address"
sig = sign_message(w, "e2e")
rec = Account.recover_message(encode_defunct(text="e2e"), signature=sig)
assert rec == w.address, "signature does not recover to signer"
ks = export_encrypted(w, "pw")
assert load_encrypted(ks, "pw").address == w.address, "encrypted roundtrip mismatch"
assert w.private_key not in str(ks), "plaintext key leaked into keystore"
print("  offline flow OK:", w.address)
PY

# 3) the MCP server entry point answers a real handshake (initialize + tools/list)
# NOTE: capture to a var first — `python - <<HEREDOC` would let the heredoc steal stdin from the pipe.
MCP_OUT=$(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | "$VENV/bin/chain-signer-mcp" 2>/dev/null)
echo "$MCP_OUT" | "$VENV/bin/python" -c '
import sys, json
tools=None; ok_init=False
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    m=json.loads(line)
    if m.get("id")==1 and m.get("result",{}).get("serverInfo",{}).get("name"): ok_init=True
    if m.get("id")==2: tools=[t["name"] for t in m["result"]["tools"]]
assert ok_init, "no valid initialize reply"
assert tools and {"create_wallet","send","swap"} <= set(tools), f"tools wrong: {tools}"
print("  MCP handshake OK:", tools)
' || fail "MCP handshake"

rm -rf "$VENV"
echo "E2E PASS (version $INST)"
