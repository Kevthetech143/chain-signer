# x402 machine/per-use payments — demand check (2026-06-01) — VERDICT: WATCH

Skeptic research (cited). The honest, important finding of the venture so far.

## Hard truths
1. Agent per-CALL x402 payments are LIVE-REAL (Firecrawl, Freepik, Nous, The Graph USDC gateway, Cloudflare pay-per-crawl). But the lane is CROWDED.
2. ACTIVE-THREAT (verified, exact-fit): the OFFICIAL x402 Python SDK — pypi `x402` v2.12.0, foundation-backed, updated 2026-05-29, 22 releases — ALREADY does local non-custodial EIP-3009 signing AND ships an `mcp` extra. Plus community signers: x402-payment-harness ("any EOA, no CDP" — verbatim our pitch), hive-rosetta, MoltsPay, ag402, x402-pay.
   => Our core differentiator "one-line non-custodial x402 signing + MCP" is COMMODITIZED. The foundation ships it free.
3. The device/EV/per-pulse wedge (our only real differentiator) has ZERO shipped evidence — vapor in blogs. EV pre-auth-hold pain is REAL ($20-100 holds, "payment anxiety") but incumbents fix it on CARD rails (incremental auth); no operator is on record wanting a crypto pay-per-pulse signer.

## My miss (own it)
I built sign_x402_payment (0.1.14) WITHOUT checking whether the official x402 SDK already does it. It does. Reuse-before-build failed at the ecosystem level. Lesson logged.

## What this means for chain-signer
- The x402-generic-signer angle is NOT a viable wedge (official SDK owns it).
- Remaining honest differentiators: (a) multi-chain breadth + burner-per-task ergonomics; (b) the hackathon's "sealed-receipt burner-per-task" (most us-only); (c) per-pulse streaming hardware payments — but UNPROVEN.
- Verdict: WATCH the device wedge. Do NOT write more x402 code. 

## Cheapest next test (one afternoon, owner call)
One honest message in x402 Telegram (~600 builders): "building a per-pulse streaming x402 signer for metered hardware (EV as exemplar) — anyone actually hitting pre-auth/custody pain on a physical device today?" If 2-3 real device-side builders say yes -> PURSUE. Else stay WATCH. No more code until a real device person expresses the pain unprompted.

Reach: x402 Telegram, x402scan.com, Merit-Systems/awesome-x402, github topic x402-payment.
