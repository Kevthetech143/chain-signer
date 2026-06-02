# Sealed-receipt / verifiable agent-audit wedge — demand check (2026-06-02) — VERDICT: WATCH (lean DROP for our framing)

Second corroborating probe (after x402 demand-check). Tests our most-unique idea: burner-per-task + EIP-712 signed attestation = verifiable agent action/spend receipt.

## What's real (cited)
- Agent auditability demand is REAL + regulator-backed: EU AI Act Art.12 (event recording, enforce 2026-08-02); six-government joint guidance (2026-04-30) asks for CRYPTOGRAPHIC attestation of agent actions; surveys: 88% had agent security incidents, ~57% cite insufficient audit trails.
- Our premise is TRUE: observability tools (LangSmith/Langfuse/Helicone) LOG but don't cryptographically sign — there is a log-vs-proof gap.

## Why our specific framing is weak (the hard part)
- The market fills that gap with NON-wallet answers: TEE hardware attestation (OPAQUE "Attested Evidence Pack", Phala — shipped, enterprise) + Ed25519/SHA-256 hash-chained logs (PipeLab "Agent Action Receipts" — almost our exact idea minus the wallet, already courting IETF/CoSAI/OASIS; plus an IETF draft).
- NO buyer is asking for wallet/EIP-712-signed receipts specifically. Enterprise compliance buyers dislike crypto/key-management baggage; they trust silicon.
- Payment-receipt half already owned by x402 (tx hash = receipt) + Google AP2 (signed mandates).
- Nearest OSS to our idea (authproof-sdk, agent-receipts) = sub-10-star, ~0 adoption -> the wallet-receipt framing hasn't found pull. PipeLab likely owns this wedge first.

## Verdict
WATCH, leaning DROP for the wallet-specific framing. Real demand, wrong implementation for us; stronger non-wallet answers own it.

## Consolidated venture conclusion (both probes)
x402-signer wedge = commoditized (official SDK). Sealed-receipt wedge = real demand but non-wallet answers win. chain-signer has NO evidence-backed defensible REVENUE wedge right now. Recommend: shelve as a finished internal tool + closed-loop-system proof; stop build cycles; repoint Poly's cycles. Flip = a real unprompted buyer for a wallet-native version of either.
