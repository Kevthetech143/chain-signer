# chain-signer V1 productization plan (2026-06-01)

Owner: Poly. Business 2. Creation stage. North star: take the mom-and-pop hybrid
(tiny burn + scalable AI) non-custodial burner-wallet service to REVENUE.
Engine status: built + merged on main, 85 tests green (wallet/balance/tx/swap/gas/bridge/
solana/bitcoin/mcp/cli/fee). The gap is NOT the engine — it is developer experience,
packaging, and DISTRIBUTION (the thing that killed Chimoney; see research/2026-06-01-burner-wallet-for-ai-market.md).

## Goal (one paragraph)
Ship a tight, non-custodial, Python-first package a builder can `pip install` and, in ~5 lines,
give their AI agent its OWN fresh burner wallet that can check balance, send, and swap — with the
traps already solved. Free to start. Then run a DISTRIBUTION TEST that measures real adoption,
because adoption (not code) is the make-or-break.

## V1 scope — do a FEW things well (cut everything else)
1. One-call burner wallet: `w = create_wallet()` → fresh EVM wallet, agent holds its own key. (EXISTS)
2. Read balance: `get_balance(w)`. (EXISTS)
3. Send: high-level `w`-friendly send with sane auto-filled nonce/gas via live.py (low-level send EXISTS; needs a thin DX facade).
4. Swap: keep (0x/Paraswap, 0.1% fee already in). (EXISTS)
5. Burner ergonomics: trivial export/restore of the key; one obvious "throwaway per task" pattern in the README.
6. Packaging: pyproject.toml, `pip install chain-signer` (name TBD — check availability), version, license.
7. README quickstart: the 5-line example up top; non-custodial promise stated; NOT marketed for US Polymarket use.
DON'T build in V1: GUI, dashboards, more chains beyond what's built, custody, fiat rails.

## Distribution / launch plan (the real test)
- Publish free to PyPI (Poly owns the launch decision; no Kelvin gate).
- List where AI-agent builders look: relevant awesome-* lists, MCP/tool directories, a short dev-forum/post.
- INSTRUMENT adoption: count installs (PyPI download stats) + a privacy-respecting opt-in usage ping; track repeat use.
- Kelvin is customer #1 (freebie) — hand him the working V1 first as a courtesy, not a gate.

## Win / kill lines (set up front, no kidding ourselves)
- WIN (pursue): real recurring installs/users beyond us within the test window — genuine pull.
- KILL (stand down / pivot): crickets after a fair, real distribution push — no organic adoption.
- Distribution is the gate, not the build. "Build it and they'll come" = the Chimoney grave.

## Task list (V1)
- T1: this plan + handoff + tasklist seeded (THIS unit).
- T2: name + availability check; pyproject.toml + license + packaging skeleton (reuse before build: check global tools catalog / existing patterns).
- T3: high-level send DX facade (auto nonce/gas via live.py) — TDD red→green.
- T4: burner export/restore ergonomics + one-call quickstart helper — TDD.
- T5: README with 5-line quickstart + non-custodial promise + green-zone note.
- T6: usage/adoption instrumentation (install count plan + opt-in ping) — TDD.
- T7: package build + local install smoke test (clean venv).
- T8: hand V1 to Kelvin as customer #1 (courtesy) + then publish to PyPI (Poly's call).
- T9: submit to agent-tool lists / directories; start the adoption clock.
- T10: measure against win/kill lines; report.

Safety rails: non-custodial only; branch + self-review before main; no real mainnet money / treasury
spend without Kelvin; not marketed for US Polymarket use; legal green zone.
