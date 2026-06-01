# Burner / programmatic wallet-for-AI market — research (2026-06-01)

Question: is "burner/disposable wallet service for AI agents" an open niche we could own?
Method: live web search this session. Evidence-first, /business-think competitor reality check.

VERDICT: NOT an open niche. As of 2026 this is a HOT, crowded, well-funded category. The exact
"non-custodial + programmatic + unlimited cheap wallet creation for agents" pitch is ALREADY shipped
by multiple active, funded players. We have no edge here on the general product.

ACTIVE-THREAT players (verified live products w/ docs, not announcements):
- Coinbase Agentic Wallets (CDP) — non-custodial, programmatic, spending caps, x402, launched ~Apr 2026.
- Openfort — CLOSEST match to our idea: non-custodial agent wallets, REST API, 25+ EVM chains,
  works w/ LangChain/CrewAI/AutoGen, "create wallet + submit tx in a few API calls." (openfort.io)
- Chimoney — IS the burner model: "create unlimited agent wallets at no cost, no monthly fee,
  pay only per transaction." Free programmatic per-task wallets already exist. (chimoney.io)
- Crossmint — full-stack agent payments, per-merchant virtual numbers, stablecoin+card rails.
- Stripe — acquired Privy (Jun 2025); Link wallet for agents, one-time-use cards / Shared Payment Tokens.
- Turnkey — hardware-enclave signing infra for agent wallets.
- Cobo, Human.tech — more entrants.
- Amazon Bedrock AgentCore payments — built w/ Coinbase + Stripe (Privy). Cloud giants embedding it.
- Directory "agentwallet.md" lists 34 programmable-wallet / agent-rail providers (2026).

Market consolidation signal (funded, real): Privy→Stripe (Jun 2025), Dynamic→Fireblocks (Oct 2025),
BVNK→Mastercard (Mar 2026). Money is pouring in = real demand, but also real incumbents.

UNVERIFIED: no per-provider wallet-creation counts or revenue found — that data isn't public.
Demand for OUR specific kit still unproven (this is category data, not us).

Implication for chain-signer: "burner wallets for AI" as a general product = crowded, no edge.
If we pursue, the reason-to-pick-us must be SHARPER than the category itself (a specific underserved
slice — e.g. a vertical the incumbents ignore, or pure-Python + specific chains). The /business-think
"dominant incumbent != closed market" rule applies BUT here there are MANY active incumbents serving
the exact need, so the bar for a real reason-to-switch is high. Lean toward TEST-CHEAPLY or STAND-DOWN
on the general burner-wallet product; revisit only with a named, narrow, underserved slice.

## Traction + revenue reality (2026-06-01, verified) — answers "do they have traffic / make money?"
- CROSSMINT (per-wallet pricing: 1,000 free Monthly Active Wallets, then $0.05/MAW + volume discounts;
  gasless, billed fiat): YES, real traffic + real money. 40,000+ companies/devs, subscription revenue
  +1,100% YoY, raised $23.6M Series A (Ribbit, Franklin Templeton, Nyca, First Round, Lightspeed) +
  Circle Ventures, 83 staff, customers incl. Mastercard, MoneyGram, Adidas. = ACTIVE DOMINANT, funded.
  (crunchbase/tracxn/blog.crossmint.com)
- CHIMONEY (the free-unlimited-wallet, pay-per-transaction, API-first BURNER model — closest to our
  planned shape): SHUT DOWN. Ceased new transactions 2026-04-30, founder confirmed closure 2026-05-12.
  Raised <$1M lifetime (~$280K). Founder's post-mortem: product worked, DISTRIBUTION killed it —
  "spent too much time building and not enough making sure customers knew what we built." Flat revenue,
  weak distribution, thin capital. (innovation-village.com, dabafinance)

LESSON (file to /business-think mindset): the per-wallet model makes money ONLY at funded/enterprise
scale with distribution (Crossmint). The exact lean model we'd ship just DIED — and died on getting
noticed, not on the build. This is hard proof that for us the make-or-break is DISTRIBUTION, not code.
Our cheap test must measure REACH/adoption first, because that is the thing that kills this category.
"Build it and they'll come" = the Chimoney grave.

## Chimoney economics dig (2026-06-01, verified) — validates the "lean / mom-and-pop + AI scale" thesis
- Revenue: never disclosed; founder said only "flat, didn't grow fast enough." Raised <$1M lifetime (~$280K).
- What actually killed them = the CAPITAL-HEAVY parts of a cross-border CUSTODIAL payments business, NOT the software:
  compliance, MSB/PSP licenses (FINTRAC + Bank of Canada RPAA), audits, 41 currencies / 3 regions,
  regulator-required liquid reserves of $1M-$10M, pre-funding payment corridors. Multi-country ops eat 15-20% of
  gross revenue; an EU EMI license alone is EUR 500K-1.2M. (thecondia, techcabal, technext24, launchbaseafrica)
- Founder's own lessons (direct quotes): "Under $1M for a venture-scale fintech across multiple jurisdictions is
  the worst of both worlds. Either raise properly or BOOTSTRAP WITH A PROFITABLE BEACHHEAD." / "I had a licensed,
  compliant, technically solid platform. I did not have a customer acquisition engine. That gap is what got us." /
  spent ~90% on product, ~10% on distribution — should've been 50/50.

KEY ASYMMETRY (file to strategy): every cost that sank Chimoney came from being a CUSTODIAL, licensed,
multi-jurisdiction money mover. Our chain-signer is NON-CUSTODIAL — we never touch funds — so we carry NONE of
those costs: no MSB/EMI license, no $1M+ reserve, no corridor pre-funding. Plus near-zero labor/office burn (AI
builds + runs it) and no investors demanding venture-scale growth. So "flat revenue" does NOT kill us the way it
killed them. Kelvin's "mom-and-pop with scalable AI" = exactly the founder's recommended "bootstrap a profitable
beachhead" path, with a cost base low enough that small real revenue is a WIN, not a death. Structural edge:
near-zero burn (like a mom-and-pop) AND scalable (AI doesn't tire) — a tier of small revenue the funded incumbents
literally can't afford to chase.
THE ONE SHARED RISK that still applies to us: distribution / customer acquisition. AI scale helps us build and
push outreach volume, but getting genuinely noticed + trusted is still the gate. That is the thing to test first.
