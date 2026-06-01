# Dev intro post (drafted by contentcreator, 2026-06-01)

Status: APPROVED asset. Owned channel done: https://github.com/Kevthetech143/chain-signer/discussions/1
Held (deliberate, not spam): MCP community Discord / GitHub Discussions + r/LocalLLaMA —
one thoughtful post each, only as a genuine participant, never a brand-new-account link-spray.

---
Give your AI agent a non-custodial burner wallet in one line

I built chain-signer because every time I wired an AI agent to do something on-chain, I hit the same wall: the agent needs a wallet, but I don't want to hand it a key I care about, and I definitely don't want some service holding funds in the middle.

chain-signer is a small Python package (pip install) that gives an agent its own throwaway wallet in a single call. The agent generates and holds its own key locally. It signs locally. Nothing routes through a custodian — I never touch your key and never touch your funds. It's non-custodial by design, not by promise.

Once the agent has a wallet, the same library does balance, send, and swap. It's also an MCP server, so any MCP-aware agent can pick it up as a tool without glue code.

Honest status: this is brand new. Zero stars. No users to brag about, no benchmarks to inflate. General-purpose tooling for agent developers — not built or marketed for any prediction-market use. I'm sharing it to get real feedback, not to chase a launch number.

The 2-second offline test — confirm the core works before trusting it with anything:

  pip install chain-signer
  python examples/quickstart.py

That makes a wallet, signs a message, and proves the signature recovers the address. No private key of yours, no funds, no network call.

It's on PyPI and listed in the official MCP registry, so it shows up for MCP-aware tooling out of the box.

If you build agents and want a clean, non-custodial wallet primitive, I'd genuinely like your eyes on it — especially the key-handling. Tear it apart.


---
POSTED (genuine, on-topic): MCP registry Show-and-tell -> https://github.com/modelcontextprotocol/registry/discussions/1327 (2026-06-01)
