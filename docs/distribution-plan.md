# chain-signer distribution plan (T9) — reach test (researched 2026-06-01)

LIVE: PyPI https://pypi.org/project/chain-signer/ (0.1.1, README renders clean) | GitHub https://github.com/Kevthetech143/chain-signer
Win = real recurring installs (tools/adoption.py) + stars/forks from strangers. Kill = crickets after a fair, honest push.

## KEY INSIGHT (live research): the buyer discovers agent tools via MCP REGISTRIES, not homepages.
We already ship an MCP server (chain_signer.mcp_server, 6 tools verified: create_wallet, get_balance, send, call_contract, swap, bridge). That makes MCP registries our highest-leverage, on-topic, non-spam channel.

## HONESTY GATE (our own /business-think rule, and maintainers enforce it):
Maintainers down-rank/flag submissions that are brand-new, 0-2 stars, single-maintainer, or mass-submitted to 15+ lists in parallel with inflated metrics. RIGHT NOW we fit that profile (repo hours old, 0 stars). So:
- DO submit to canonical, namespace-verified registries where a fresh entry is legitimate (official MCP registry; Glama auto-index).
- DO NOT spray awesome-lists yet — that flags us "unverified" and burns credibility. Earn a little real traction first.
- Never inflate metrics. State true numbers or none.

## Sequenced targets (one at a time, honest)
1. server.json manifest — DRAFTED (repo root). Points to PyPI 0.1.1, stdio transport, GitHub namespace io.github.kevthetech143.
2. Official MCP Registry (registry.modelcontextprotocol.io) — canonical. Needs `mcp-publisher` CLI + GitHub-namespace auth (gh authed as Kevthetech143). NEXT real step; validate server.json vs the live schema first (training cutoff — confirm fields).
3. Glama (glama.ai/mcp) — auto-indexes open-source MCP servers from GitHub; repo is public; verify it gets picked up.
4. mcp.so — submit via GitHub issue ("Submit"): name, 1-line capability, tool count (6), transport (stdio), repo URL, homepage.
5. Smithery (smithery.ai) — `smithery mcp publish` or web dashboard.
6. THEN (after some traction): awesome-mcp-servers PR (now requires a Glama listing first), e2b-dev/awesome-ai-agents, kyrolabs/awesome-agents — single, well-targeted, accurate.
7. One honest dev.to write-up: "give your agent a non-custodial burner wallet in one line."

## Done already
- GitHub topics added (ai-agents, wallet, non-custodial, web3, agent-tools, python).
- PyPI keywords/classifiers set; README renders on the PyPI page (verified markdown, 3.4k chars).

## Measure (T10): tools/adoption.py weekly; log installs + stars; verdict vs win/kill.

## MILESTONE (2026-06-01): LISTED ON OFFICIAL MCP REGISTRY ✅
io.github.Kevthetech143/chain-signer v0.1.3 is live at registry.modelcontextprotocol.io (confirmed via API search). PyPI 0.1.3 carries the mcp-name ownership marker. This is the highest-leverage, on-topic discovery channel — agents find tools here. Adoption clock STARTS now.
Next honest channels (no spam): Glama auto-index (verify pickup), mcp.so submit, Smithery. Awesome-lists held until real traction.


## CORRECTION (verified 2026-06-01): auto-propagation did NOT happen.
Earlier I noted directories auto-ingest from the official registry (no manual submits needed). VERIFIED FALSE for Glama + mcp.so: hours after our official-registry listing, neither shows chain-signer. (A mcp.so URL 200s for any slug — a false positive; our markers Kevthetech143/non-custodial/burner are absent.) So manual submission IS needed. Action taken: filed a single, accurate mcp.so submission via the intended path (github.com/chatmcp/mcpso issue #2605). NOT spam — one real submission to the canonical directory. Glama/Smithery + an awesome-mcp-servers PR remain as deliberate single submissions (the 2026 'four directories' guidance), held until we also have a little traction for the PR.
