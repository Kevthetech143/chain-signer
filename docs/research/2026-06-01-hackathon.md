# Hackathon — creative uses of chain-signer (2026-06-01)

8 hacker agents (distinct angles) -> code-sketch a real use -> 3 judges each (creativity/feasibility/grounded/surprise) -> 3 grounded survivors. Full raw: 2026-06-01-hackathon-raw.json.

## Standouts (all judge-flagged SURPRISE, feasible today)
1. WINNER (7.5) — EV charger per-kWh x402 micropayment. The car's agent signs a tiny x402 authorization PER 0.1 kWh pulse; the signature IS the meter's permission to keep delivering. Pay only for energy already in the battery; halt by withholding the next signature. Gasless (EIP-3009 sign-only) until the charger batches settlement. Named paying pain: curbside/fleet operators hate pre-auth holds + chargeback-prone custodial billing.
2. (7.17) — Sealed-receipt burner-per-task. Spawn a fresh burner per agent job; it signs an EIP-712 attestation of exactly what it did + spent. The throwaway key doubles as a notary; the address is the task's primary key = self-contained, tamper-proof audit trail. (Uniquely leverages OUR burner + sign_typed_data combo; broader than x402.)
3. (6.5) — Bounty escrow handshake. Buyer agent pre-signs a future-dated, capped x402 auth that becomes spendable only after the worker returns a pre-committed result. Payment signature = settlement receipt; collapses escrow into one signed auth.

## Honest read
- Worth a real demand-check: the EV/machine per-use payment idea — concrete operator pain, real x402 fit. Run the evidence-hunt pattern on it before building anything.
- Sealed-receipt is the most "us-only" idea (burner + local typed-data attestation) and is a cheap, differentiated helper if demand shows.
- The two agent-to-agent ideas are elegant but presuppose an autonomous-agent commerce market that isn't liquid yet.

## Note on a judge false-strike
A judge worried sign_typed_data / sign_x402_payment might be private. They are PUBLIC exports as of 0.1.13 / 0.1.14 (the agents likely read a stale installed copy). No feature gap — version-alignment artifact only.
