# Transaction Preflight — plan (2026-06-02) — chain-signer's real wedge

GOAL: before chain-signer signs an EVM tx, tell the agent what it DOES + flag danger. Turns "raw keys are risky" (the knock that beat our wallet wedge) into our differentiator: "the agent signer that won't sign a dangerous transaction."

## API (one function, wraps the existing send path)
preflight(tx, *, fetch=None, sim=None) -> report:
  report = {
    "decoded": {function, args, to, value} | None,   # ABI/4byte decode of calldata
    "risk_flags": [ {code, severity, detail} ],       # the danger list
    "simulation": {will_revert: bool, balance_changes, error} | None,
    "ok": bool                                        # true if no HIGH flags
  }
Wire into the signer: build tx -> preflight(tx) -> if HIGH flags and caller didn't override -> refuse/return warning -> else sign+broadcast. Opt-in param on send (preflight=True).

## Risk rules (each = one TDD unit, independently testable)
1. unlimited/large ERC-20 approval (approve(spender, ~uint256max)) -> HIGH
2. setApprovalForAll(true) (NFT) -> HIGH
3. delegatecall / op=1 in the path -> HIGH
4. recipient is a NEW/unverified/never-seen address (heuristic; injectable lookup) -> MED
5. native value transfer above a caller threshold -> MED
6. will_revert (simulation says it fails) -> HIGH
7. decode failure / opaque calldata to a contract -> LOW (warn "can't tell what this does")

## Engine
- Decode: eth_abi + eth_utils + a 4byte fallback (function selector -> signature). Reuse eth_account/our codecs.
- Simulate: default = pure-Python static checks (decode + rule match) with NO network (works offline, deterministic, testable). Optional richer sim via injectable `sim` (pyrevm in-process if available, or an RPC eth_call/trace) — keep it injectable so tests need no chain.
- NO new hard deps if avoidable: eth_abi/eth_utils/eth_account already present (verified). pyrevm is OPTIONAL (only used if installed + requested).

## TDD order
Unit per rule (1-7), each a red test with a crafted tx -> green rule. Then the send-path integration (preflight=True refuses on HIGH). Then README hero rewrite + ship via tag.

## Non-goals (v1)
No full mainnet fork sim required; no custody; no auto-fixing the tx — we WARN, the agent/user decides.
