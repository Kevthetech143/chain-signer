# chain-signer viability — business-think verdict (2026-06-01)

## VERDICT: STAND-DOWN as a build-investment → shift to WATCH/measure.
Stop spending build cycles. The product is done, sound, listed. Let the adoption clock (≤2026-07-01)
or one real inbound decide. Do NOT ship more features into a commoditized space.

## Why (evidence-first)
- Competitor reality check:
  - OFFICIAL x402 SDK (pypi x402 v2.12.0, foundation-backed, mcp extra, updated 2026-05-29) = ACTIVE-THREAT, exact hit on our core (free non-custodial signing + MCP). Strongest possible commoditizer.
  - Coinbase AgentKit / Crossmint GOAT / Turnkey = ACTIVE-THREAT on the broad agent-wallet lane.
  - x402-payment-harness / hive-rosetta / MoltsPay = real, small, but prove the signer is trivial/free.
- Room + reason-to-switch: ROOM yes (agent payments growing, live endpoints). REASON-TO-SWITCH: none VERIFIED. Every candidate edge — non-custodial, Python, MCP — the official SDK also has. Multi-chain breadth + sealed-receipt are UNVERIFIED hypotheses, not demonstrated pulls.
- Traction: 0 users, 0 stars after a fair honest push (official MCP registry + mcp.so + awesome-x402 PR + community post). That's the kill signal the win/kill lines named.

## The single thing that would FLIP it → PURSUE
One real, unprompted builder/user expressing a need our SPECIFIC differentiator serves — a multi-chain (Solana/Bitcoin) agent wallet, or the per-task sealed-receipt audit trail — that the official SDK does NOT give them. Get it via the queued community post + the running adoption clock. NOT via more code.

## What chain-signer still IS (not a failure)
- A finished, listed, hardened tool that can still get discovered for free (zero burn to keep live).
- A successful proof of the closed-loop build system: idea→viability→TDD build→publish→registry→hands-free CI→adversarial stress-test→demand-hunt→hackathon→honest kill-check. That system is the reusable win for the portfolio (/venture-cycle).

## Systemic note (to Primary/Kelvin)
The 15-min "BUILD PUSH" cron now conflicts with the evidence (stop building). Recommend throttling it to a slow WATCH cadence (e.g. 1-2x/day: check stars/installs/PR/inbound, run E2E, report only on change) until a flip signal. Building every 15 min into a commoditized space burns tokens for no return.

## 2026-06-02 — WEDGE HUNT (Kelvin "find a reason"): DROP, premise was false
Verified the non-EVM/multi-chain lead. It FAILS:
- My "x402 SDK is EVM-only, Solana is the gap" premise is FACTUALLY WRONG: the official Coinbase x402 SDK ships CAIP-2 multi-network incl. Solana (6 SVM e2e tests; Coinbase facilitator settles Solana); Solana joined the x402 Foundation (Apr 2026) and led ~65% of x402 volume.
- Solana agent-wallet niche is already OWNED: SendAI Solana Agent Kit (TS+Python, 100k+ downloads, 1,400 stars) is the default; Coinbase AgentKit (CdpSolanaWalletProvider), Crossmint GOAT (Python, multi-chain), Turnkey (SVM+BTC+EVM, one call), MoonPay Agents (EVM+SOL+BTC+TON+Tron, PayPal/Circle-backed), Privy all cover it in production.
- Bitcoin-agent demand is thin (CoinDesk May 2026: little commercial activity); non-custodial BTC slot also taken (Turnkey/MoonPay/Privy/Trust Wallet).
- Our raw-local-key design is on the WRONG side of the documented pain ("raw key in agent code is dangerous"); market answer is MPC/TEE/enclaves — opposite of ours.
VERDICT: DROP. No defensible reason-to-switch exists. Disarmed the wedge-hunt cron (71baa0cd) per its own honesty gate. chain-signer stays a finished/listed tool + the closed-loop build proof; new energy -> caregiver venture (real demand).
