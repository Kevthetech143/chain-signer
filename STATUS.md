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
- [x] Step 5 — Red tests — 7 failing tests for wallet + key-secrecy invariant (pure unit). Committed.
- [x] Step 5b — Red-test review — ACCEPTED. 3 independent reviewers (behavioral, coverage, runtime) all PASS after one fix round.
- [x] Step 6 — Green code — non-custodial Wallet via eth_account; 9/9 tests pass. Committed.
- [x] Step 6b — Green review — ACCEPTED. Both reviewers (implementation integrity + anti-pattern) PASS.
- [ ] Step 7 — Review-work audit
- [ ] Step 8 — Package tool + local control API
- [ ] Step 9 — Live test EVERY function end-to-end + bonus real wallet-to-wallet transfer (see DEFINITION OF DONE)
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
4. UNIVERSAL APP INTERACTION (reaffirmed 2026-05-31): the tool must let an agent interact with ANY app on a supported
   chain by signing whatever that app needs — exactly like we interact with Polymarket (an app on Polygon). So
   call_contract / program-call is a first-class ability, not optional. EVM (Polygon/ETH) + Solana = full app+contract
   interaction. Bitcoin caveat: Bitcoin is NOT an app platform like the others — it mostly moves coins with limited
   scripting; real "apps" live on add-on layers. On Bitcoin we support transfers + its scripting, not full apps. Flagged to Kelvin.

## Research findings (brief: docs/research/2026-05-31-landscape.md)
- Best reuse base: MoonPay Open Wallet Standard — non-custodial (agent holds key), open-source, Python, MCP/Claude-ready.
- Day-one chains: 9 families incl Ethereum, Solana, Bitcoin. KLEVER: not supported by anything — we'd build that signing path ourselves.
- Fee capture (swaps): pass integrator-fee params to an existing DEX aggregator that routes our cut — we never hold funds. Stays non-custodial.
- Legal: non-custodial + never holding keys/funds = NOT a money transmitter under the main federal (FinCEN) rule. Biggest risk is a broader criminal-law reading (Tornado Cash precedent: founder convicted partly for running the front-end others used). Staying non-custodial + not operating others' funds keeps exposure lowest. (Research, not legal advice.)

## Open decision for Kelvin
Custody + fee model: NON-CUSTODIAL + tiny per-tx fee (he confirmed). 
KLEVER AT LAUNCH? Default = defer Klever to phase 2; launch on EVM + Solana + Bitcoin via the MoonPay standard.
If Klever is required at launch, add a from-scratch Klever signing path (extra build). Override if needed; else review-plan proceeds on the default.

## NEXT ACTION (cron: read this first)
The tool has SEVERAL functions; each is its own red→green→review slice (pipeline Steps 5→6b repeat per slice).
Steps 7-9 (review-work, package, live-test-everything) run ONCE all slices exist — do NOT jump to them early.
Slices 1-2 DONE through green-review. NEXT = Slice 3 (send) red tests.

## SLICES
1. [x] wallet — create/own key, address, key-secrecy invariant. DONE (9 tests green, both reviews pass).
2. [x] get_balance — read balance from the LIVE chain via Etherscan v2 (read-only). DONE (4 tests green, red+green reviewed).
3. [ ] send — build/sign/post a transfer (Polygon Amoy testnet). NEXT.
4. [ ] call_contract — sign/post an app/contract interaction (testnet).
5. [ ] swap + fee — DEX-aggregator swap with our 0.1% integrator fee (prove on mainnet fork).
6. [ ] mcp_server — expose the contract so any AI can call it.

## Known limitations to harden later (not blocking this slice)
- The private key sits in the instance __dict__, so vars()/pickle could expose it. No code path does this and no
  function logs it, but a later hardening slice should add a redaction test (vars()/pickle must not reveal the key).
- get_balance does not check Etherscan's status field; an API error payload raises on int() instead of a clear
  message. Add a red test + clear error in a hardening slice.

## DEFINITION OF DONE (Kelvin 2026-05-31) — the cron's "are you done yet?" bar
The 15-min cron asks "are you done yet?" each cycle. The answer is YES only when ALL of these are true:
1. Tool FULLY BUILT — every planned function implemented (create wallet, read state, send, call_contract/app, swap-with-fee).
2. FULLY TESTED — full test suite green.
3. LIVE TEST — a real run on a live network confirms EVERY function works (not just unit tests).
4. BONUS PROOF — a real wallet-to-wallet crypto transfer executed with crypto we actually hold (TINY amount on Polygon).
Until all four are true, the answer is "not yet" + the one thing blocking. Then report merge-ready and delete the cron.

Note on #4: this is the ONE step that touches REAL funds. Kelvin pre-approved it (2026-05-31). Keep it tiny, use crypto
we already hold on Polygon (deposit wallet 0x0a94...), and report the tx hash before+after. Everything else stays testnet.

## Heartbeat
A 15-min cron (id 14a00c11) drives the next pending step, runs tests, reports status each cycle, and self-ends only
when the DEFINITION OF DONE above is fully met.
Spec: ~/agents/global/cron/polymarket/chain-signer-build.md
