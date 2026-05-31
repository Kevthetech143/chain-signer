# chain-signer — Landscape Research Brief

Date: 2026-05-31
Scope: non-custodial, multi-chain transaction signing tool for AI agents, monetized by a tiny per-tx fee.
Status: research synthesis only. Section 4 is NOT legal advice.

---

## 1. Recommended reuse base

Lead with MoonPay Open Wallet Standard (OWS). It is the only option that hits all four requirements in one package: genuinely non-custodial (the agent never sees the key — AES-256-GCM at rest, decrypt-sign-wipe in an isolated process), MIT licensed, first-class Python SDK bindings, and a built-in MCP server interface. It spans 8 chain families and enforces spending policy (limits, allowlists, chain/time restrictions) at the wallet layer.
- https://www.moonpay.com/newsroom/open-wallet-standard

Runner-up: GOAT SDK (Crossmint). MIT, TypeScript + Python, local-keypair non-custodial wallets for EVM and Solana, 200+ prebuilt tools, and the widest exotic-chain coverage. Use it if exotic chains matter more than Python+MCP convenience — its MCP adapter is TypeScript-only, so you would wrap it yourself for Python.
- https://github.com/goat-sdk/goat/blob/main/README.md
- https://github.com/goat-sdk/goat

Avoid as the base:
- Coinbase AgentKit — default custody is MPC/server-side (CDP); non-custodial is only a side path, and it is Base-centric. https://github.com/coinbase/agentkit/blob/main/python/coinbase-agentkit/README.md
- Base MCP — forces human-in-the-loop confirmation in the Base App; cannot sign unattended. https://news.bitcoin.com/base-launches-mcp-gateway-letting-claude-and-chatgpt-execute-onchain-defi-actions/
- thirdweb — server-custody KMS, EVM-only. https://github.com/thirdweb-dev/ai/tree/main/python/thirdweb-mcp

Use only if you want hardware-grade signing and will build the wallet + MCP layer yourself:
- Turnkey — TEE enclave signing, even Turnkey cannot read raw keys, but it is signer infrastructure, not a finished agent tool. https://www.turnkey.com/solutions/ai-agents

---

## 2. Chains we can hit day-one vs later

Day-one (native in OWS, one seed across families):
- EVM, Solana, Bitcoin, Cosmos, Tron, TON, Spark, Filecoin, XRP Ledger.
- https://www.moonpay.com/newsroom/open-wallet-standard

Later / build-it-yourself:
- Exotic chains (Aptos, Sui, Starknet, MultiversX, Radix, etc.) — not in OWS; available via GOAT SDK if we add it. https://github.com/goat-sdk/goat
- Klever — honest gap: NONE of the surveyed toolkits support Klever natively. GOAT covers MultiversX (Klever's tech cousin) but not Klever. Klever's own MCP servers are knowledge/RAG and scaffolding only — they explicitly do NOT sign or hold keys. A Klever signing path must be built separately on @klever/sdk-node (JS/TS), klever-go-sdk (Go), or kos-rs (Rust) and bridged in. There is no official Python Klever signer to reuse. https://mcp.klever.org/

---

## 3. Simplest non-custodial fee-capture design

Pick by what the tool does:

If it swaps/trades tokens — ride the 0x Swap API v2 integrator-fee parameters. Set swapFeeBps (up to 1000 bps), swapFeeToken (the buy or sell token), swapFeeRecipient (our wallet). 0x routes our cut to our address inside the same settlement transaction. No contract to deploy, no funds held.
- https://0x.org/docs/0x-swap-api/guides/monetize-your-app-using-swap
- Fallback: 1inch (ReferrerAddress + percentage, or integratorFee in bps on Fusion). Rejects fee-on-transfer tokens; adds its own infra fee. https://portal.1inch.dev/documentation/faq/infrastructure-fee

If it charges per request/action (not a swap) — use x402 with EIP-3009/USDC on Base. One-line payment middleware; the facilitator only broadcasts the client's pre-signed transfer and never holds funds. Point the payment recipient at our fee wallet directly, or use an x402 proxy+Hook scheme to split a percentage atomically. Plain transferWithAuthorization cannot embed a markup.
- https://github.com/coinbase/x402
- https://github.com/coinbase/x402/blob/main/specs/schemes/exact/scheme_exact_evm.md

Avoid for v1: custom fee-router contracts, ERC-4337 paymasters (couples fee to gas sponsorship), and fee-on-transfer wrappers (only work on tokens we mint, break DeFi accounting, reentrancy risk).
- https://osec.io/blog/2025-12-02-paymasters-evm/
- https://mixbytes.io/blog/defi-patterns-erc20-token-transfers-howto

Dependency to watch: Coinbase's hosted x402 facilitator charges $0.001/tx after 1,000 free/month from Jan 1 2026 — run our own facilitator if that matters.
- https://docs.cdp.coinbase.com/x402/core-concepts/facilitator

---

## 4. Biggest legal risk + how non-custodial reduces it

NOT legal advice — confirm with a crypto-regulatory attorney before launch.

A tool that only lets users sign their own transactions, where we never hold their keys or funds, is NOT a money transmitter under FinCEN's controlling 2019 guidance — even with a small per-tx fee, because the test turns on custody/control (acceptance plus transmission), not on how we are paid.
- https://www.fincen.gov/resources/statutes-regulations/guidance/application-fincens-regulations-certain-business-models
- https://www.fincen.gov/resources/statutes-regulations/administrative-rulings/application-fincens-regulations-persons

Biggest live risk is the criminal statute 18 U.S.C. Section 1960, which a court may read more broadly than FinCEN's custody-based test. In the Tornado Cash case, Roman Storm was convicted Aug 6 2025 of conspiracy to run an unlicensed money-transmitting business; prosecutors leaned on the team maintaining the front-end UI most users went through. The boundary is unresolved — Lewellen v. Bondi was dismissed March 25 2026 on standing without ruling on the merits, and is on appeal.
- https://www.moneylaunderingnews.com/2025/08/tornado-cash-jury-deadlocked-on-most-serious-charges-but-convicted-founder-roman-storm-on-conspiracy-to-operate-an-unlicensed-money-transmitting-business/
- https://blockchain.bakermckenzie.com/2026/04/01/federal-court-dismisses-crypto-developers-pre-enforcement-challenge-relating-to-his-crowdfunding-tool/

How strict non-custodial design lowers the risk:
- Never hold keys or funds; never be able to unilaterally execute or block a transaction.
- Keep settlement strictly peer-to-peer between users.
- Segregate the fee flow so user principal never routes through us.
- Add no mixing/anonymizing feature (it gets no safe harbor).
- Keep architecture and flow-of-funds docs proving custody-out from day one.
- https://www.fincen.gov/system/files/2019-05/FinCEN%20CVC%20Guidance%20FINAL.pdf

DOJ's April 2025 Blanche memo and the Aug 2025 Galeotti remarks lean in the non-custodial operator's favor, but they are non-binding policy that can be reversed.
- https://www.justice.gov/opa/speech/acting-assistant-attorney-general-matthew-r-galeotti-delivers-remarks-american

---

## 5. Top 3 open questions for Kelvin

1. Is Klever support a launch requirement or a later add? If launch, we must budget a separate signing bridge (no off-the-shelf Python path exists). https://mcp.klever.org/
2. What does the tool actually do at v1 — swaps, or per-request/action charges? That single answer picks the fee design (0x params vs x402-on-Base). https://0x.org/docs/0x-swap-api/guides/monetize-your-app-using-swap
3. Do we host our own UI/front-end? The Tornado Cash conviction leaned on the team running the front-end most users passed through — a thinner front-end footprint lowers criminal exposure. https://www.moneylaunderingnews.com/2025/08/tornado-cash-jury-deadlocked-on-most-serious-charges-but-convicted-founder-roman-storm-on-conspiracy-to-operate-an-unlicensed-money-transmitting-business/
