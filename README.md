# chain-signer

<!-- mcp-name: io.github.Kevthetech143/chain-signer -->

![PyPI](https://img.shields.io/pypi/v/chain-signer) ![Python](https://img.shields.io/pypi/pyversions/chain-signer) ![License](https://img.shields.io/pypi/l/chain-signer) ![Release](https://github.com/Kevthetech143/chain-signer/actions/workflows/release.yml/badge.svg)


A non-custodial agent wallet with a preflight safety check. Give your AI agent its own
wallet in one line, and a first-line guard that decodes a transaction and flags common drain
patterns BEFORE it signs — unlimited approvals, approve-all, token & NFT transferFrom pulls,
proxy upgrades, on-chain permit, approvals hidden inside multicall (including Uniswap-style router
batches), and reverts. It's a guard, not a guarantee (it won't catch permit-signature phishing,
which isn't a transaction), and it fails safe — it flags rather than waving through what it can't
read. Make a burner wallet, check balance, send, swap; the agent holds its own key and signs
locally. No MetaMask, no account, no custody.

```python
from chain_signer import assert_safe
assert_safe(tx)   # raises if the tx is a drain/unlimited-approval/revert — review before signing
```

## Install
```
pip install chain-signer
export ETHERSCAN_API_KEY=...   # for live balance reads + broadcast (Etherscan v2)
```
Bitcoin/Solana support is optional: `pip install "chain-signer[all]"`.

## Quickstart (5 lines)
```python
from chain_signer import burner, send_ether
from chain_signer.balance import get_balance

w = burner()                          # fresh throwaway wallet; the agent owns w.private_key
print(w.address, get_balance(w))      # live on-chain balance
send_ether(w, "0x...recipient", 0.001)  # auto nonce+gas, signed locally, broadcast
```
That's it — your agent just held a wallet and moved funds, no human in the loop.

### Try it offline in 2 seconds (no key, no funds, no network)
```
pip install chain-signer
python examples/quickstart.py   # makes a wallet, signs, proves it recovers + encrypts the key
```

## Safety preflight (the wedge)
Before an agent signs, hand the unsigned tx to `preflight()` — it decodes the calldata and returns
the risks, or use `assert_safe()` to hard-stop on a HIGH flag. Offline, no network, never raises.
```python
from chain_signer import preflight, assert_safe

# an unlimited-allowance approve() to a spender — the classic drain setup
tx = {"to": token, "data": "0x095ea7b3" + spender_padded + "f"*64, "value": 0}

report = preflight(tx)
# {'decoded': {...}, 'ok': False,
#  'risk_flags': [{'code': 'unlimited_approval', 'severity': 'HIGH',
#                  'detail': 'approve() grants an effectively-unlimited allowance ...'}]}

assert_safe(tx)          # raises ValueError on a HIGH flag; pass force=True to override
assert_safe(tx, sim=my_simulator)   # optional: also flag will-revert via your simulation hook
```
What it flags today: unlimited/large approval, `increaseAllowance`, `setApprovalForAll`,
ERC-20 `transferFrom` + ERC-721/1155 `safeTransferFrom` (token & NFT drains), on-chain `permit`,
proxy `upgradeTo`/`upgradeToAndCall`, approvals hidden inside `multicall` (all router variants,
nested), large native value, opaque calldata, malformed calls, and will-revert (with a sim hook).
Honest limits: it can't read intent it can't decode, and off-chain permit-signature phishing flows
through `sign_typed_data`, not a transaction — so that's out of scope. A guard, not a guarantee.

## What you get
- `preflight(tx)` / `assert_safe(tx)` — decode an unsigned tx and flag drain patterns before signing (the wedge).
- `burner()` — a fresh wallet for a one-off task; discard it when done.
- `restore(key)` — reload a wallet later from its exported private key (same key → same address).
- `send_ether(w, to, amount)` — send in ETH (not wei); nonce, gas, and broadcast handled for you.
- `get_balance(w)` — live balance from the chain (Etherscan v2 indexer, not a flaky public RPC).
- `swap(...)` — token swaps via 0x/Paraswap.
- Optional Solana + Bitcoin wallets via the `[all]` extra.

## Non-custodial guarantee
The private key is generated/loaded locally, used only to sign, and never logged, returned, or
stored by this library. You hold the key; we never touch your funds. That is the whole design.

## Handling the key (read this)
`w.private_key` is the keys to the wallet. Treat it like a password:
- NEVER log it, print it in production, or write it into notes/memory/chat. Anyone who has it controls the funds.
- For a burner holding a few dollars this is low-stakes by design — but the rule still holds.
- To reuse a wallet later, store the key in a secret manager / env var, then `restore(key)`.
- Better: `export_encrypted(w, password)` gives a password-protected keystore dict to store at rest; `load_encrypted(keystore, password)` brings the wallet back. Never store the raw key if you can store the keystore.

## Signing idiom (note for web3.py users)
The wallet does not expose `sign_transaction` / `sign_message` methods. Signing is done by
function helpers you pass the wallet to — e.g. `send_ether(w, to, amount)` signs and broadcasts,
and `sign_message(w, "text")` returns an EIP-191 signature for auth / sign-in flows
(recoverable via eth_account `Account.recover_message`).

## CLI on PATH
`pip install` may warn that the `chain-signer` script dir isn't on your PATH. The library works
regardless; to use the CLI directly, add that dir to PATH or run `python -m chain_signer ...`.

## Tool surface (for any AI / MCP / CLI)
`chain_signer.mcp_server` exposes `list_tools()` and `call_tool(name, arguments)`. CLI:
```
python -m chain_signer list
python -m chain_signer call create_wallet '{"chain":"evm"}'
```

## Responsible use
General-purpose, non-custodial tooling. You are responsible for using it within the laws and
terms of service that apply to you. Not intended or marketed for any restricted or prohibited
trading in your jurisdiction.

## Notes
- Balances/broadcast use the Etherscan v2 indexer (authoritative), never a free public RPC.
- Low-level building blocks (`tx.send`, `call_contract`, explicit nonce/gas) remain available for advanced use.

## Pay an x402 API in one call
```python
from chain_signer import burner, sign_x402_payment
w = burner()
payload = sign_x402_payment(w, token=USDC, to=PAY_TO, value=1000, valid_before=EXPIRES, chain_id=8453)
# -> {"signature", "authorization"} ready for the x402 payment header. Signed locally, no prompt.
```
Builds + signs the EIP-3009 authorization x402 expects (the "exact" scheme). Your agent pays a
paid API by itself — no password prompt, no signup, no custody.

## Sign typed data (EIP-712) — for agent payments / x402
```python
from chain_signer import burner, sign_typed_data
w = burner()
sig = sign_typed_data(w, domain, types, message)  # EIP-712; for x402 / EIP-3009 authorizations
```
Your agent can authorize a payment by signing typed data locally — no password prompt, no signup.

## Run as an MCP server
chain-signer is also a Model Context Protocol (MCP) server, so MCP-aware agents can use it directly:
```
pip install chain-signer
chain-signer-mcp          # speaks MCP over stdio (JSON-RPC 2.0)
```
Exposes 6 tools: create_wallet, get_balance (balance), send, call_contract, swap, bridge.

Wire it into any MCP client (Claude Desktop, Cursor, etc.) by adding it to the client's
`mcpServers` config:
```json
{
  "mcpServers": {
    "chain-signer": {
      "command": "chain-signer-mcp",
      "env": { "ETHERSCAN_API_KEY": "your-key-for-live-balance-and-broadcast" }
    }
  }
}
```
That's all — the agent can now make a wallet, read balances, send, and swap as native tools.
(`ETHERSCAN_API_KEY` is optional; needed only for live balance reads and broadcasting.)
