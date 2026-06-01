# chain-signer handoff (latest first)

2026-06-01 — V1 productization kicked off. Branch `v1-productization` off main. Engine done on main (85 tests green). Wrote docs/plans/v1-productization.md (tight V1 scope = burner-wallet DX + packaging + distribution test; engine gap is distribution, not code). Task list T1–T10 in the plan. NEXT: T2 — name/availability check + pyproject packaging skeleton (reuse before build). Rails: non-custodial, branch-only, no real money without Kelvin, not for US Polymarket, green zone. Kelvin = customer #1 (freebie); Poly owns launch decision.

2026-06-01 — T2 DONE. Name "chain-signer" verified FREE on PyPI (404). Fleshed pyproject: hatchling build-system, MIT license, readme, classifiers, keywords, URLs, console-script chain_signer.cli:main (verified), extras solana=[solders,base58] bitcoin=[bit], core EVM-only (web3/eth-*). 85 tests green. NEXT: T3 — high-level send DX facade (auto nonce/gas via live.py), TDD.
