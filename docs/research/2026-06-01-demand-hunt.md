# Demand hunt — verified findings (2026-06-01)

Method: 6 parallel evidence lanes -> 37 findings -> 14 verified adversarially -> 12 confirmed real+cited.
Full raw: docs/research/2026-06-01-demand-hunt-raw.json.

## The wedge (verified, cited) — LEAD WITH THIS
x402-paying terminal/coding agents (Claude Code, Gemini, Cursor) need a NON-INTERACTIVE local key.
- 0xKoda/x402-wallet exists for this exact pain: encrypted keystores "Block automation" + "Break AI
  agent workflows — agents cannot enter passwords interactively." Our one-call create-wallet removes
  that structurally (not a marketing claim). https://github.com/0xkoda/x402-wallet
- Positioning: "The local burner wallet for agents that pay x402 APIs — one call to create, signs
  with no password prompt, no signup, no dashboard." Testnet/burner/minimal-funds first.

## Other real, reachable pockets
2. Ask HN (id=47736831, 17pts/16 comments): builders asking "is it safe to give an agent a key, what
   to use?" — no default exists. Reach: one honest reply.
3. MCP-wallet gap: no pip-installable, non-custodial, create-a-wallet MCP server found
   (nikicat/mcp-wallet-signer, wallet-agent are import-only/TS/testnet-warned). Reach: r/mcp, registry.
4. Incumbent-bounced devs: Coinbase AgentKit CDP gate (api keys, no EVM local-key path), Turnkey
   enterprise/TEE gate. We win on lightness for throwaway/testnet, NOT production custody.
5. Live agent swarms with plaintext keys: AutoHedge (3k+ stars, Solana, WALLET_PRIVATE_KEY in .env),
   ElizaOS/ai16z ($25M AUM, keys in env). Adjacent; wedge = provisioning + burner ergonomics.

## HONEST RISK (counter-evidence — guardrail, do not ignore)
Google Cloud: raw-local-key model is "very high risk... mainly for testing." Incumbents own the
"non-custodial BUT safe" lane via MPC (Coinbase) / TEE (Turnkey). So: NEVER claim production safety.
Lead burner/testnet; put spend caps + scoped keys on the roadmap to grow credibility.

## Reality of the signal
Real but SMALL: x402-wallet 4 stars, mcp-wallet-signer 1 star, HN 17 pts. Proves friction is felt by
real builders; does NOT prove a big market yet. Early-adopter wedge, not a gold rush.

## Demand-justified product next (no longer speculative)
x402 payments need EIP-712 typed-data / EIP-3009 transferWithAuthorization signing. We only ship
EIP-191 (sign_message). Adding sign_typed_data is the feature the verified wedge actually requires.

## Next non-spam actions (queued)
A. PR to xpaysh/awesome-x402 + submit to mcpserverfinder (discovery; audience self-selects).
B. One honest, useful reply on Ask HN id=47736831 (answer the question; mention us with scope stated).
C. Genuine PR/issue on 0xKoda/x402-wallet offering the pip/MCP-native variant.
