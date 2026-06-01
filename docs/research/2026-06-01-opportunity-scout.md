# Cross-chain opportunity scout — verdict (2026-06-01)

Method: 16-agent fan-out (5 scout lanes + adversarial verify + synth). Decision-only, live data, honest-after-costs.
Thesis confirmed: the tool is REACH, not EDGE. At ~$5-150 capital + one wallet + seconds-scale speed, no
cross-chain money-maker survives honest scrutiny.

SURVIVED (small):
- Polymarket Taker Rebate (live 2026-05-28): a few % back on fees we already pay + one-time ~$10 lowest-tier bonus.
  Not income — free because we already take liquidity there. NEXT: confirm Bronze terms, enable on existing wallet.
- Jupiter Lend USDC on Solana ~4.8% APY (large/stable pool) — safe parking for idle dollars (~$4/yr on $100), not a strategy.

DIED under scrutiny:
- Cross-chain price gaps (WETH/PENDLE/GMX/RDNT): zero at our size or fake (thin-pool slippage); bridge+gas eat it; MEV-contested.
- Stablecoin yield routing (Fluid/Spark): pennies at our capital; some lose to risk-free T-bills.
- Other prediction markets (Drift/Limitless/Myriad): wrong chain / wrong edge type / US-blocked; no wording seam.
- Copy-trading (Solana memecoins / Nansen on Base): we arrive seconds late = exit liquidity; useful data is paywalled past our bankroll.

Implication: real income needs an EDGE (information/speed/capital) the tool doesn't grant. Best uses remain (1) point our
existing research edge at the bigger surface as finds arise, (2) low-risk self-treasury (idle USDC -> Jupiter Lend),
(3) the free Polymarket rebate. Stand down on speculative cross-chain plays at this capital.

## Decision panels (2026-06-01) — pursue as revenue product?
/council: NO, unanimous 3-0. /congress: FAIL, 5-0 NAY. Veto check flagged money-transmission exposure (fees on others' tx).
Consensus: do NOT productize now — trust + distribution gap vs free/audited/funded incumbents (Crossmint, Coinbase), not a feature gap.
Flip conditions: real users, an audit, OR a downstream business of our own. Until then: use chain-signer INTERNALLY (agent fleet on-chain autonomy) — cheap, real, no compliance burden. Advisory; Kelvin decides.

## Productize-as-DIY-kit — REAL evidence (2026-06-01, sourced; replaces earlier assumptions)
- Agent-wallet SDK market consensus: USE the free open-source SDKs (Coinbase AgentKit, Crossmint GOAT); don't build/buy the wallet layer. (agentwallet.md, openfort.io)
- Devs PAY for the bundle we DON'T have: compliance/licensing/KYC + card/payment rails + spending controls (e.g. Crossmint full-stack, EU-licensed). Not the wallet primitive.
- Boilerplate/kit sales reality: active market but long-tail — one transparent seller ~$2,539/yr, 80% of products ~zero, breakout ~$734/105 sales, ~5% email conversion; established kits (MakerKit) took years + marketing/docs/social proof. (medium income breakdown; dodopayments)
- Evidence-based read: paid DIY wallet kit sits on the commoditized free layer; comparable kits mostly earn little without an audience we lack. Scarce paid layer = compliance+rails (big build, not our edge).
- STILL UNVERIFIED: demand for OUR specific kit (this is comparable-market data, not us).
NOTE: earlier "no one will pay / trust gap / pocket change" were ASSUMPTIONS; Kelvin flagged it; role rule 'evidence_over_assertion_when_planning' added (v12).

## /business-think competitor reality check (2026-06-01, VERIFIED traction — corrects earlier headline read)
- Coinbase AgentKit: ACTIVE THREAT — @coinbase/agentkit 40,659 npm dl/mo, pushed 2026-05-28, 1241*.
- Crossmint GOAT: ACTIVE THREAT but TS-only — @goat-sdk/core ~11,916 npm dl/mo; PyPI goat-sdk just 211 dl/mo (Python barely served); pushed 2026-05-30, 993*.
- Polymarket/agents (official): 3614* BUT pushed 2024-11-05 = ABANDONED ~19mo. Headline rival, dead in reality. (The exact catch.)
- caiovicentino/polymarket-mcp-server (active Polymarket trading MCP): pushed 2026-06-01, 534*, single maintainer = ACTIVE but NICHE/small.
- MoonPay MoonAgents / Trust Wallet TWAK / Turnkey: UNVERIFIED (closed products; announcements, no adoption numbers pulled) — not counted as confirmed threats.
VERDICT: general wallet space = won by AgentKit/GOAT (stand down head-on). Prediction-market vertical in PYTHON = NOT crowded (official tool dead, active one tiny, GOAT Python near-empty) = real narrow opening. -> TEST-CHEAPLY-FIRST: publish a focused Python Polymarket/prediction-market agent kit (BYO-wallet, traps solved) to PyPI + MCP/awesome-polymarket lists; measure pulls. Flip-to-pursue: real downloads/users. Flip-to-standdown: crickets or caiovicentino MCP already covers it well (check its fit next).
NOTE: this corrects the earlier headline-driven STAND-DOWN; verified data moved it to TEST-FIRST on the vertical.
