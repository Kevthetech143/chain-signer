# chain-signer — build status

Product: a universal on-chain transaction tool. Any AI agent creates/owns a wallet and signs + posts
transactions directly across chains (swap, buy/sell, transfer, contract call, explore) — no MetaMask, no GUI.
Non-custodial: the agent holds its own key, exactly like MetaMask. Monetize via a tiny per-transaction routing fee.

Origin: proven on 2026-05-31 — we already sign + post directly to the Polygon chain for Polymarket with our own
private key (no Polymarket account, no browser). This generalizes that.

## Pipeline (build-express discipline, adapted for greenfield)
- [x] Step 0 — Research & close knowledge gaps — DONE. Brief: docs/research/2026-05-31-landscape.md
- [ ] Step 1 — Think-first (architecture)
- [ ] Step 2 — Write plan → docs/plans/chain-signer.md
- [x] Step 3 — Review-plan GATE — PROCEED. Decisions locked (fee 0.1%, new collector wallet, EVM-first, fork-proof). Kelvin delegated the calls 2026-05-31.
- [ ] Step 4 — TDD pre-recon
- [ ] Step 5 — Red tests
- [ ] Step 5b — Red-test review
- [ ] Step 6 — Green code
- [ ] Step 6b — Green review
- [ ] Step 7 — Review-work audit
- [ ] Step 8 — Package tool + local control API
- [ ] Step 9 — Verify end-to-end on Polygon testnet (NO real money)
- [ ] Step 10 — Merge (Kelvin go-ahead)

## Hard rules
- Non-custodial only. We never hold a user's key or funds. (Lowest legal exposure; matches the MetaMask model.)
- No real money during the build. Polygon testnet only until verified.
- Reuse before build: wrap an existing open-source engine (GOAT / AgentKit) + our Polygon recipe. Do not rebuild a signer.
- Branch + commit per unit of work. Never push to main. Merge on Kelvin's explicit go-ahead.
- Stop at any gate that needs Kelvin: review-plan verdict, anything touching real funds, custody, legal, or merge.

## Kelvin's locked requirements (2026-05-31)
1. Production-ready tool (not a demo).
2. Built-in fee: OTHER users pay a very small, tiny fee that does NOT stop them from using it.
3. Acceptance: I must PROVE it works by using it myself (dogfood — I create a wallet with it and post a real transaction).

## Research findings (brief: docs/research/2026-05-31-landscape.md)
- Best reuse base: MoonPay Open Wallet Standard — non-custodial (agent holds key), open-source, Python, MCP/Claude-ready.
- Day-one chains: 9 families incl Ethereum, Solana, Bitcoin. KLEVER: not supported by anything — we'd build that signing path ourselves.
- Fee capture (swaps): pass integrator-fee params to an existing DEX aggregator that routes our cut — we never hold funds. Stays non-custodial.
- Legal: non-custodial + never holding keys/funds = NOT a money transmitter under the main federal (FinCEN) rule. Biggest risk is a broader criminal-law reading (Tornado Cash precedent: founder convicted partly for running the front-end others used). Staying non-custodial + not operating others' funds keeps exposure lowest. (Research, not legal advice.)

## Open decision for Kelvin
Custody + fee model: NON-CUSTODIAL + tiny per-tx fee (he confirmed). 
KLEVER AT LAUNCH? Default = defer Klever to phase 2; launch on EVM + Solana + Bitcoin via the MoonPay standard.
If Klever is required at launch, add a from-scratch Klever signing path (extra build). Override if needed; else review-plan proceeds on the default.

## Heartbeat
A 15-min cron drives the next pending step, runs tests, reports status, and self-ends when Step 9 passes.
Spec: ~/agents/global/cron/polymarket/chain-signer-build.md
