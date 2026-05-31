# Plan review — chain-signer (2026-05-31)

Verdict: REVISE (gate — awaiting Kelvin).

Senior verdict: MODIFIED. Plan directionally sound; base must be spike-proven; "swap+fee" was over-generalized
across chains; fee size missing.

Key changes applied to the plan:
- EVM-first v1 (prove the whole loop on Polygon, the chain we own); Solana/Bitcoin → phase 1.5; Klever → phase 2.
- Per-chain capability honesty (Bitcoin has no contract_call/aggregator swap).
- Aggregators don't run on testnets → prove fee-bearing swap on a local mainnet FORK (Anvil), or tiny real-mainnet under Kelvin's go.
- Added: gas-funding (faucet/user), real RPC provider (free public RPCs lie), tx-confirmation/nonce, key storage (gitignored).
- Reuse: copy-adapt our Polygon recipe for the EVM adapter (NEW project, no catalog yet).

Blockers (need Kelvin): fee size (number), collector wallet, Klever-at-launch?, approve EVM-first, approve fork-proof, distribution.

Test-contract: satisfied via hand-off to /tdd-write-redtest against /tdd-pre-recon (pipeline Steps 4-5).
