# Plan — chain-signer

## Goal
A production-ready, non-custodial, multi-chain transaction tool that any AI agent can call to: create and
own a wallet, read chain state, and sign + post transactions (transfers, token swaps, arbitrary contract
calls) across multiple chains — with no MetaMask and no GUI. Every swap is routed through an existing DEX
aggregator with a tiny built-in integrator fee paid by the user to our fee-collector address; we never take
custody of anyone's keys or funds. The tool is exposed to agents as a Python library plus an MCP server so any
AI (including this one) can drive it. Acceptance is by dogfooding: the tool itself creates a wallet and posts a
real transaction on a testnet (then mainnet on Kelvin's explicit go-ahead).

## Files in scope (greenfield repo at ~/agents/chain-signer/)
- pyproject.toml, README.md, .gitignore (ignore keys/.env)
- chain_signer/__init__.py — public API surface
- chain_signer/wallet.py — non-custodial key create/load, address; key held locally by caller, never logged/stored/transmitted
- chain_signer/chains/evm.py — EVM adapter (reuses our proven Polygon recipe: sign, approve-gas, USDC.e nuance)
- chain_signer/chains/solana.py — Solana adapter
- chain_signer/chains/bitcoin.py — Bitcoin adapter
- chain_signer/chains/klever.py — DEFERRED (phase 2)
- chain_signer/tx.py — build/sign/post transfers and contract calls
- chain_signer/swap.py — DEX-aggregator swap with built-in integrator fee
- chain_signer/fee.py — fee config + collector address
- chain_signer/mcp_server.py — MCP tool surface
- tests/ — unit + contract + testnet integration

## Approach (numbered)
1. git init the repo; commit a scaffold + .gitignore on a feature branch. Never commit secrets.
2. Dependency spike (de-risk first): install the chosen base — MoonPay Open Wallet Standard (fallback: GOAT SDK) —
   and PROVE it works by creating a throwaway testnet wallet and reading a balance, before building on it. Pick the
   base by what actually works, read from the live source, not from the research summary alone.
3. Define the stable public contract: create_wallet, get_address, get_balance, send, swap, call_contract, explore —
   chain-agnostic signatures.
4. wallet.py — non-custodial key handling. Key generated/held locally by the calling agent. No path persists,
   logs, or transmits a user key. This invariant is tested.
5. EVM adapter first, reusing our proven Polygon signing recipe. Prove on Polygon Amoy testnet.
6. swap.py — built-in tiny integrator fee via DEX-aggregator params; fee routes to our collector address; assert we
   never hold the funds.
7. Add Solana + Bitcoin adapters via the base standard.
8. mcp_server.py — expose the contract so any AI (including me) can call it.
9. Dogfood acceptance: the tool creates a wallet and posts a real transfer + a fee-bearing swap on testnet, driven
   by me; capture on-chain tx hashes as proof. Mainnet only on Kelvin's go.
10. Klever: phase 2 (from-scratch signing path) unless Kelvin requires it at launch.

## Test contract (what tests pin)
- create_wallet returns a valid address; the private key NEVER appears in any return value, log, or stored file.
- get_balance equals on-chain truth (read live, never a cache).
- send builds, signs, and posts a transfer; returns a real tx hash; testnet balance changes accordingly.
- swap routes through the aggregator with the integrator fee attached; the fee lands at the collector address; the
  tool's process never holds the swapped funds (custody-invariant assertion).
- the fee is non-zero but tiny and does NOT block the swap (swap still succeeds end-to-end).
- call_contract signs and posts an arbitrary contract interaction.
- multi-chain: the same public contract works on EVM, Solana, and Bitcoin adapters.

## Open questions (need Kelvin before/at the gate)
- Klever at launch, or phase 2? (default: phase 2)
- Fee size — how tiny? Needs an actual number (e.g. basis points). Cannot guess.
- Fee-collector wallet — a NEW dedicated address (recommended) or reuse an existing one?
- Distribution at launch — Python library + MCP only (lower legal profile), or also a hosted API later?
- Testnet for the dogfood proof — Polygon Amoy proposed.
