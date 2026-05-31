# Pre-recon — chain-signer (2026-05-31)

## Environment (measured this session)
- Python 3.12.8; web3 7.16.0 + eth_account INSTALLED. solders (Solana) NOT installed (phase 1.5).
- foundry/anvil NOT installed (needed only for the mainnet-fork swap proof — install when we reach swap).
- Our Polygon recipe present: ~/agents/polymarket-brain/tools/auto_fire_bot.py, poly_exec.py, wallet_state.py.
- Read/data API: Etherscan v2 key (chainid=137 + 60 EVM chains) in tools/web3/polygon-apis.md. Source of truth for balances/tx.
- Candidate SDKs pip-available: goat-sdk 0.1.6, coinbase-agentkit 0.7.4.

## Senior simplification (reuse-before-build)
EVM v1 needs NO new SDK. web3.py + eth_account + copy-adapt of our proven Polygon recipe IS the EVM adapter.
GOAT / AgentKit / MoonPay-standard become relevant only in phase 1.5 (Solana/Bitcoin), where we have no recipe.
This drops a heavy dependency from the critical path and builds v1 on the most-proven ground we have.

## Peer pattern to copy
auto_fire_bot.py (order recipe: sign, nonce, gas, post, confirm) and wallet_state.py (live balance via Etherscan v2,
never free public RPC — they return false zeros). The EVM adapter mirrors this shape for generic transfer/contract_call.

## Build order (de-risked: pure-unit first, network later)
1. Scaffold repo (pyproject, package, README). 
2. FIRST slice — NO network needed: wallet.py (key gen/load, address) + the public contract + the custody-invariant
   (key never logged/stored/returned). Red tests here are pure-unit and fully runnable now.
3. EVM read: get_balance via Etherscan v2 (live truth).
4. EVM write: send + call_contract on Polygon Amoy testnet — needs an Amoy RPC + faucet POL for gas (see gaps).
5. fee.py + swap.py — prove on a mainnet fork (needs foundry/anvil installed).
6. mcp_server.py.

## Environment gaps to close (none are real-money/custody/legal — I handle them)
- Amoy testnet RPC endpoint (public rpc-amoy.polygon.technology likely fine) — confirm at the write step.
- Testnet POL for gas — request from a faucet (may use the /web skill). Free play-money, not real funds.
- Install foundry/anvil before the swap-fork step.
- No dedicated Alchemy/Infura key — Etherscan v2 proxy module can broadcast; confirm it covers Amoy, else use public Amoy RPC.

## Test contract handoff
Red tests written via /tdd-write-redtest. First slice (wallet + custody invariant) is pure-unit, network-free.
