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

## Approach (numbered) — REVISED after review (EVM-first sequencing)
v1 proves the WHOLE loop on the one chain family we already own (EVM/Polygon). Multi-chain is phase 1.5.
This delivers all three of Kelvin's requirements (production-ready, built-in fee, dogfood proof) on proven ground first.

1. git init; commit scaffold + .gitignore on a feature branch. Never commit secrets. keys/ is gitignored.
2. Dependency spike (de-risk FIRST): install the candidate base — MoonPay Open Wallet Standard, fallback GOAT SDK —
   and PROVE it from the live source by creating a throwaway testnet wallet and reading a balance. The base is chosen
   by what actually works, not by the research summary. Also confirm a real RPC provider (NOT a free public RPC — those
   return false zeros) and a testnet faucet for gas.
3. Define the public contract: create_wallet, get_address, get_balance, send, call_contract, swap, explore.
   Capabilities VARY by chain (e.g. Bitcoin has no call_contract) — the contract advertises per-chain capability,
   it does not pretend every op works everywhere.
4. wallet.py — non-custodial key handling. Key generated/held locally by the calling agent. No code path persists,
   logs, or transmits a user key. This invariant is the crown-jewel test.
5. EVM adapter, COPY-ADAPTING our proven Polygon recipe (polymarket-brain/tools/auto_fire_bot.py, poly_exec.py):
   sign, nonce, gas, approve, tx-confirmation polling. Prove transfer + contract_call on Polygon Amoy testnet.
6. fee.py + swap.py — tiny integrator fee via an EVM DEX aggregator (0x Swap API integrator-fee, or 1inch). Fee routes
   to our collector address; assert the tool never holds the swapped funds. NOTE: aggregators do not run on testnets —
   prove the fee-bearing swap on a LOCAL MAINNET FORK (Anvil forking Polygon mainnet: real liquidity, no real money),
   or a single tiny real-mainnet swap under Kelvin's explicit go.
7. mcp_server.py — expose the contract so any AI (including me) can call it.
8. Dogfood acceptance (v1): the tool creates a wallet and posts a real transfer + contract_call on Amoy testnet, plus
   the fee-bearing swap on the mainnet fork; capture tx hashes / fork traces as proof. Real mainnet only on Kelvin's go.
9. Phase 1.5: add Solana (Jupiter referral fee) and Bitcoin (no swap/contract — transfer only) adapters.
10. Klever: phase 2 (from-scratch signing path) unless Kelvin requires it at launch.

## Test contract (what tests pin)
- create_wallet returns a valid address; the private key NEVER appears in any return value, log, or stored file.
- get_balance equals on-chain truth (read live, never a cache).
- send builds, signs, posts a transfer; returns a real tx hash; testnet balance changes accordingly.
- call_contract signs and posts an arbitrary contract interaction (EVM).
- swap routes through the aggregator with the integrator fee attached; the fee lands at the collector address; the
  tool's process never holds the swapped funds (custody-invariant assertion). Proven on the mainnet fork.
- the fee is non-zero but tiny and does NOT block the swap (swap still succeeds end-to-end).
- capability honesty: calling an unsupported op for a chain (e.g. call_contract on Bitcoin) raises a clear error.
- test steps hand off to /tdd-write-redtest against the /tdd-pre-recon doc (Step 4/5 of the pipeline).

## Closed-loop pattern verdict
NEW project — no chain-signer CATALOG.md yet. Canonical reuse: our Polygon signing recipe
(polymarket-brain/tools/auto_fire_bot.py, poly_exec.py) for the EVM adapter — copy-adapt, do not reinvent.
Run /patterns-reuse + /audit-patterns when code begins.

## Risks & mitigations (from review)
- Aggregators not on testnets → prove swap+fee on Anvil mainnet fork or tiny real-mainnet under Kelvin's go. (HIGH)
- Fresh wallet has zero gas → testnet faucet; mainnet user funds own gas. (MED)
- Free public RPCs return false zeros → use a real RPC provider. (MED)
- Base may not deliver Python+MCP as summarized → spike verifies; fallback GOAT SDK. (MED, UNVERIFIED until spike)
- Legal: non-custodial keeps us out of money-transmitter rule; this is research, not legal advice. (tracked)

## Open questions — NEED KELVIN (plan gate: REVISE until answered)
1. Fee size — how tiny, exactly? Needs a number (basis points or %). Cannot be guessed.
2. Fee-collector wallet — a NEW dedicated address (recommended) or reuse an existing one?
3. Klever at launch, or phase 2? (default: phase 2)
4. Approve EVM-first v1 sequencing (multi-chain in phase 1.5)?
5. Approve proving the fee-bearing swap on a mainnet FORK (no real money), with a real-mainnet test only on your go?
6. Distribution at launch — Python library + MCP only (lower legal profile), or also a hosted API later?
