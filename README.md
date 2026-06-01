# chain-signer

Give your AI agent its own non-custodial wallet in one line. Make a fresh (burner) wallet,
check balance, send, and swap — your agent holds its own key and signs locally. No MetaMask,
no browser, no account, no custody.

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

## What you get
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
