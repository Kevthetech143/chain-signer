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
