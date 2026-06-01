# chain-signer — Venture Pipeline (reference instance for /venture-cycle)

This is the lived end-to-end journey of Business 2 (chain-signer), the reference instance the
`/venture-cycle` skill points at. Real receipts, real gotchas, real stage status. Updated every
cron session. Copy this shape for a new venture; don't start blank.

What chain-signer is: a non-custodial, Python-first burner-wallet + tooling kit for AI agents —
make a fresh wallet in one call, check balance, send, swap, bridge. The agent holds its own key;
we never touch funds. Mom-and-pop hybrid: near-zero burn + scalable AI.

## Stage status (live)
- Stage 0 Frame — DONE. docs/operating-doctrine.md.
- Stage 1 Viability — DONE. /business-think verdict: PURSUE as a tight one-line-burner wedge; competitors mostly free/funded but the throwaway-wallet niche + non-custodial + multi-chain-by-default is a real seam. Edge is thin → sharpen via DX + distribution.
- Stage 2 Plan — DONE. docs/plans/ + tasklist. Win line = real recurring installs from strangers + stars/forks. Kill line = crickets after a fair, honest push.
- Stage 3 Closed loop — DONE. Brain + pillars.md (Distribution / Security / Competition) at ~/agents/polymarket-brain/businesses/02-chain-signer/.
- Stage 4 Build V1 — DONE. TDD throughout; suite 115 green. Wallet/balance/send/call_contract/swap/bridge + sign_message + encrypted-at-rest keystore. Real MCP stdio server with typed tool schemas.
- Stage 5 Package & publish — DONE. Live on PyPI (0.1.0 → 0.1.4), each verified by clean-venv install. Sequence: ~/agents/global/tools/version-control/pypi-publish-sequence.md.
- Stage 6 Agent-discoverable — DONE. Listed on the official MCP registry: io.github.Kevthetech143/chain-signer (confirmed live via API). Sequence: ~/agents/global/tools/version-control/mcp-registry-publish-sequence.md. Hands-free CI proven: a git tag publishes to PyPI (Trusted Publishing) + registers on the registry (GitHub OIDC), zero tokens/taps. Live at 0.1.7 on both.
- Stage 7 Distribution / demand — IN PROGRESS. Official registry auto-propagates to PulseMCP/mcpindex/Glama. Holding awesome-lists until real traction (honesty gate). GitHub repo public with discovery topics.
- Stage 8 Measure vs win/kill — IN PROGRESS. tools/adoption.py reads pypistats (lags ~1d for new packages). No verdict yet — adoption clock just started 2026-06-01.
- Stage 9 Feed the loop — ONGOING. This file + handoff.md + the two saved sequences above + the /venture-cycle skill.

## Reusable assets this venture produced (saved for other ventures)
- PyPI publish sequence → global tools catalog (above).
- MCP-registry publish sequence → global tools catalog (above).
- The /venture-cycle skill itself (idea → viability), ~/.claude/skills/venture-cycle/.
- Pattern: package = library + real MCP stdio server sharing ONE typed tool surface (mcp_server.TOOL_SPECS as source of truth; mcp_stdio wraps it).

## Next planned units
- CI/CD: GitHub Actions + PyPI Trusted Publishing (OIDC) + registry GitHub OIDC → hands-free releases, no device taps, no token expiry.
- Stage 8: first real adoption read once pypistats populates; verdict vs win/kill.
