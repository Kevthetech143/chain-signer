# Chain-signer operating doctrine (Kelvin, 2026-06-01)

Build-through-walls, zero-hire, zero-spend. I (Poly) run this venture autonomously with AI.
When we hit a wall, we BUILD the solution — we do not hire and we do not spend money.
Need a feature, a security review, a distribution pipeline, a dashboard, a test harness? Build it.
Near-zero burn is the moat (see 2026-06-01-burner-wallet-for-ai-market.md cost asymmetry).

THE HONEST LIMIT (walls that are NOT code-shaped — don't pretend "build it" solves these):
- DEMAND / ATTENTION: we can build the outreach pipe, but cannot code people into caring or trusting.
  This wall is crossed by TESTING + earning real users, not by writing more code. (Chimoney died here.)
- TRUST: earned over time, not built in a sprint.
- LEGAL / CUSTODY / REAL-MONEY lines: decision walls needing Kelvin's sign-off + staying non-custodial,
  not a script. Respect them, don't "build through" them.
For those three, "build it" becomes "test it / earn it / respect it." Everything else: build it.

## Three pillars (track every cycle)
This venture also keeps ~/agents/polymarket-brain/businesses/02-chain-signer/pillars.md with three live sections: Distribution, Security, Competition. Read it each cycle; when new intel lands (a real install number, a security fix, a competitor move), update the matching pillar. Stale pillars = silent risk. Current standouts: Distribution = the real gate (PyPI is a listing, not distribution); Security = V1.1 must-fix the plain private_key (encrypted-at-rest + keychain) before any real-funds tier; Competition = wedge is thin (one-line burner) — sharpen via multi-chain-by-default + drop-in framework module.

## PIPELINE + reuse upkeep (every cron session — added 2026-06-01)
This venture is the reference instance for the /venture-cycle skill (idea -> revenue-viability end to end).
Each cron fire: update docs/PIPELINE.md (stage progress + any new receipt/gotcha) AND append a short founder's-log entry to docs/JOURNEY.md (the WHY behind the cycle's moves). If a new reusable tool Keep journal entries BRIEF and direct — 1-3 short lines, the WHY only, no narrative.
sequence or workflow was built this cycle, SAVE it for reuse — command playbook -> ~/agents/global/tools/<category>/,
code pattern -> /audit-patterns, workflow skill -> /skill-transfer — then link it in /venture-cycle and PIPELINE.md.
Stale pipeline = lost compounding. Skill: ~/.claude/skills/venture-cycle/skill.md. Saved sequences:
~/agents/global/tools/version-control/{pypi-publish-sequence,mcp-registry-publish-sequence}.md

## Adoption scoreboard (T10): append a dated row to docs/ADOPTION.md when checking signals; honor the concrete WIN/KILL lines set there (verdict ~2026-07-01).

## E2E product test every 5 fires (Kelvin 2026-06-01): each fire run `bash tools/e2e_gate.sh`; if it prints RUN, spawn a tester subagent (Agent/general-purpose) to run `bash tools/e2e_smoke.sh` (installs the LIVE PyPI package in a clean venv; wallet+sign+recover+encrypt + MCP handshake). Log PASS to docs/ADOPTION.md; on FAIL, notify Kelvin immediately.
