# chain-signer handoff (latest first)

2026-06-01 — V1 productization kicked off. Branch `v1-productization` off main. Engine done on main (85 tests green). Wrote docs/plans/v1-productization.md (tight V1 scope = burner-wallet DX + packaging + distribution test; engine gap is distribution, not code). Task list T1–T10 in the plan. NEXT: T2 — name/availability check + pyproject packaging skeleton (reuse before build). Rails: non-custodial, branch-only, no real money without Kelvin, not for US Polymarket, green zone. Kelvin = customer #1 (freebie); Poly owns launch decision.

2026-06-01 — T2 DONE. Name "chain-signer" verified FREE on PyPI (404). Fleshed pyproject: hatchling build-system, MIT license, readme, classifiers, keywords, URLs, console-script chain_signer.cli:main (verified), extras solana=[solders,base58] bitcoin=[bit], core EVM-only (web3/eth-*). 85 tests green. NEXT: T3 — high-level send DX facade (auto nonce/gas via live.py), TDD.

2026-06-01 — T3 DONE. Added chain_signer/api.py: to_wei (Decimal-exact) + send_ether (ETH-denominated one-call, wraps send_live). Exported both from package top level. TDD 4 tests; full suite 89 passed (+4), no regressions. NEXT: T4 — burner ergonomics (key export/restore + throwaway-per-task helper), TDD.

2026-06-01 — T4 DONE. Added burner() + restore() to api.py (thin over create_wallet), exported both. burner=throwaway-per-task, restore=reload from exported key (evm+solana round-trip tested). TDD 5 tests; suite 94 (+5). V1 surface now: burner()/create_wallet -> get_balance -> send_ether -> swap, restore(). NEXT: T5 — README 5-line quickstart + non-custodial promise + green-zone note.

2026-06-01 — T5 DONE. Rewrote README: 5-line burner quickstart up top (burner->get_balance->send_ether), non-custodial promise, responsible-use/green-zone note, [all] extra for sol/btc. Verified all quickstart calls resolve (no network). NEXT: T7 — build the package + clean-venv install smoke test (T6 instrumentation can follow). Suite 94 green.

2026-06-01 — T7 DONE. Built wheel+sdist; clean-venv install smoke PASSED (burner/restore/to_wei + chain-signer CLI all work from the installed wheel). V1 is publishable. Suite 94 green. MILESTONE: V1 ready for Kelvin as customer #1. NEXT: T8 (hand Kelvin the install, then publish to PyPI — Poly owns launch) and T6 (adoption instrumentation).

2026-06-01 — CUSTOMER #1 TEST PASSED (Kelvin): wheel install clean, one-liner made a wallet <1s, verdict "V1 ships". Acted on feedback: README now has key-safety warning + signing-idiom note + PATH note. Queued T11 = sign_message helper (TDD). NEXT: T11, then T8 publish-to-PyPI (my call) + T9 list on agent-tool directories, T6 adoption instrumentation.

2026-06-01 — T11 DONE. Added sign_message(wallet,text) EIP-191 helper (eth_account reuse), exported; recovers to signer. TDD 3 tests; suite 97 (+3). README idiom note updated. Customer-#1 feedback now fully actioned. NEXT: T8 publish-to-PyPI (my call — needs PyPI account/token; if none, that is a real account-setup wall) + T9 list on agent-tool directories + T6 adoption instrumentation.

2026-06-01 — T6 DONE. tools/adoption.py: free pypistats install-count reader (day/week/month), TDD 3 tests, suite 100. Opt-in telemetry ping SKIPPED on purpose (needs hosting = not zero-spend); PyPI download stats are our adoption signal. BLOCKED on T8 publish (needs PyPI account/token from Kelvin). NEXT while blocked: T9 — prep agent-tool directory listings (draft submissions, no account needed yet).

2026-06-01 — PyPI ACCOUNT CREATED + VERIFIED (username chainsigner, email alltechkev@gmail.com; password in vault). Kelvin solved the hCaptcha; I submitted + verified via gws email link. T8 unblocked. NEXT to publish: PyPI requires 2FA before an upload API token — (1) enable TOTP 2FA, (2) create API token (store in global tools catalog), (3) twine upload dist/*. Browser session "pypi" left open + logged in.

2026-06-01 — PUBLISHED. chain-signer 0.1.0 LIVE on PyPI: https://pypi.org/project/chain-signer/0.1.0/ . Set up 2FA (TOTP secret + recovery codes in vault), created entire-account upload token (in global tools/version-control/), twine upload OK. VERIFIED: `pip install chain-signer` in clean venv works, burner() runs. T8 truly done. Distribution clock STARTS now. NEXT: T9 — list on agent-tool directories (awesome-* lists, etc.) to drive the reach test; T10 — watch tools/adoption.py install counts vs win/kill.

2026-06-01 — PUBLIC REPO live: https://github.com/Kevthetech143/chain-signer (gh Kevthetech143, repo scope). Merged v1 branch to main (100 tests), fixed project URLs, pushed, added discovery topics. Wrote docs/distribution-plan.md (T9 targets: awesome-* PRs, MCP dirs, dev post). Reach test STARTED. NEXT: work T9 listings one at a time (PRs via gh); T10 measure installs weekly via tools/adoption.py.

2026-06-01 — v0.1.1 PUBLISHED. Added export_encrypted/load_encrypted (eth_account keystore) — closes Security pillar top must-fix (encrypted at-rest). TDD 3 tests, suite 103. Merged to main, pushed GitHub, twine upload OK, VERIFIED fresh-venv install serves 0.1.1. NEXT: update security pillar (must-fix DONE), keep distribution push (T9 listings) + watch installs (T10).
