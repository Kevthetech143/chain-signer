# Agent Security Suite — business direction (set 2026-06-03 by Kelvin)

## What this business is
A focused SECURITY toolkit for AI agents, under ONE brand. The wedge, in one line:
"Don't let an AI agent do something dangerous." Depth in agent-transaction/action security —
NOT breadth (we do NOT compete with Coinbase/official kits on general wallets).

Brand: PROVISIONAL — working name "agent-security suite" (lock the real brand name later; cheap
to change at 0 users). Each tool = its own clean, standalone, dependency-light package under the
one brand/identity, so reputation compounds across the suite and any tool works with any wallet.

## Goal
Be the leader in agent transaction/action security — the trusted "seatbelt" layer that pairs with
every agent wallet + identity stack (AP2 / Skyfire / Coinbase / Okta). Complement, not compete.

## The lineup (build toward it; each tied to an EVIDENCED pain, never a guess)
1. Transaction preflight (FLAGSHIP — shipped, in chain-signer): decode an unsigned EVM tx + flag
   drain patterns before signing. Keep hardening. Extract to a standalone lightweight package when
   it sharpens adoption (chain-signer keeps it as a dependency).
2. Signed-message / permit-phishing inspector: the off-chain EIP-712 / Permit2 SIGNATURE scam our
   tx-guard structurally can't catch (documented gap). Real, evidenced (top drain vector).
3. Action-policy gate: enforce allow/forbid rules before an agent tool call. The "auth isn't enough,
   inspect what the agent DOES" half EVERY identity vendor named (Cisco/CrowdStrike/Okta + NIST 2026).
(+ more ONLY when a real user asks or a new evidenced pain appears.)

## Operating doctrine (binding)
- Evidenced pains only — no speculative tools. Cite the pain before building.
- Reuse before build; zero-hire, zero-spend; non-custodial; legal green-zone.
- TDD red->green per unit; hands-free ship pipeline (git tag vX.Y.Z -> PyPI + MCP registry).
- DISTRIBUTION RUNS IN PARALLEL with build. Inventory does NOT summon customers — reach does.
  Stocked shelves + no foot traffic = no sales. Keep pushing honest reach every cycle too.
- 3 pillars tracked each cycle: Distribution (real stars/forks/installs, not download noise),
  Security (adversarially test — these are security tools, correctness is the product),
  Competition (stay non-overlapping; we are the complement to identity/wallet stacks).

## LIVE-VERIFY RULE (Kelvin, 2026-06-03 — binding)
After EVERY ship (tag pipeline green), spawn a SUB-AGENT to install the LIVE PyPI package in a fresh
venv and exercise all tools end-to-end (preflight drain, permit/Permit2/DAI signatures, action-gate
fail-closed, MCP introspection lists the tools). Unit tests passing is NOT enough — only call it
shipped-verified when the published artifact works for a real installer. Tests prove the repo; this
proves what users get.
