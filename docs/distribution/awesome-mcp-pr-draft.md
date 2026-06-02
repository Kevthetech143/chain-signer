# awesome-mcp-servers PR — ready to fire on Kelvin's go

Target list: punkpeye/awesome-mcp-servers (88k stars, maintained; last push 2026-05-27).
Account: Kevthetech143 (real, since 2024-10; thin standing — clears spam bar via merit, not clout).
Contributing rules (read 2026-06-02): follow existing format/style; categorize appropriately; MAINTAIN ALPHABETICAL ORDER within the category; accurate + concise descriptions.

## Category decision
Both fit; pick ONE primary (list convention = one category):
- SECURITY (recommended) — our wedge is the preflight guard. Real peers there are agent guardrail/policy tools that check risk before a tool executes (Acacian/aegis "risk assessment + approval gates"; agentward-ai "enforces policy on every tool call"; arian-gogani/nobulex "no proof, no transaction"). chain-signer's "flag drains before signing" sits exactly in that neighborhood — and it's how we WANT to be discovered.
- FINANCE & FINTECH (alternate) — real peers: non-custodial wallets/signers/agent-payment tools (Logitale non-custodial, Arbitova non-custodial escrow, yieldagentx402 custody-free signing). Fits "it's a wallet," but buries the safety wedge among generic wallets.

## Draft entry (honest, leads with the wedge, matches format)
- [Kevthetech143/chain-signer](https://github.com/Kevthetech143/chain-signer) 🐍 🏠 🍎 🪟 🐧 - Non-custodial multi-chain agent wallet (EVM/Solana/Bitcoin) with a transaction preflight that decodes unsigned EVM calldata and flags drain patterns — unlimited approvals, approve-all, transferFrom, proxy upgrades, on-chain permit, multicall-hidden approvals — before the agent signs. A first-line guard, not a guarantee; fails safe. `pip install chain-signer`

Emoji rationale: 🐍 Python · 🏠 local/self-hosted stdio server · 🍎🪟🐧 cross-platform (pure Python). No 🎖️ (not an official protocol impl), no ☁️ (runs locally).

## Placement
Alphabetical by repo path within the chosen category. "Kevthetech143/chain-signer" sorts among the K entries.

## Fire sequence (one go, after Kelvin approves wording + category)
1. `gh repo fork punkpeye/awesome-mcp-servers --clone` (into a temp dir)
2. Insert the entry line in the chosen category, alphabetical position.
3. Branch `add-chain-signer`, commit "Add chain-signer (non-custodial agent wallet with tx preflight)".
4. `gh pr create` with a 2-line body: what it is + the safety wedge + pip/MCP install.
5. Report PR URL to Kelvin; log to JOURNEY + pillars; start the adoption clock (task T9/T28).

HONESTY GATE: ONE well-fit list first. Do NOT mass-submit to many lists from a 0-star repo — that reads as spam and burns the account. Earn a little traction, then a second list.
