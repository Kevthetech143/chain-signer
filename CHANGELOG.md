# Changelog

All notable changes to chain-signer. Newest first. Security fixes are released as a new version —
published versions are never overwritten. Dates are UTC.

## 0.5.7 — 2026-06-03
- Docs/positioning: the MCP registry listing now leads with the security suite and names all three
  guards (was wallet-led, naming only the preflight check). No code change.

## 0.5.6 — 2026-06-03
- Docs/positioning: PyPI summary and keywords now lead with the security wedge (preflight,
  permit-phishing, action-gate) instead of "burner-wallet"; added a `Topic :: Security` classifier.
  Improves organic discoverability for the actual use case. No code change.

## 0.5.5 — 2026-06-03
- Security (preflight): an approval/drain hidden in a `multicall` nested **beyond** the depth cap
  was returning a soft advisory, so `assert_safe()` did not hard-stop it. Abnormally deep nesting is
  not a legitimate pattern — it is now flagged HIGH (`deeply_nested_multicall`) so the hard stop
  fires. Real multicalls nest 1–2 deep, so false-positive risk is negligible.

## 0.5.4 — 2026-06-03
- Security (inspect_typed_data): DAI-style `permit` was only flagged when `allowed` was the boolean
  `True`. A hostile dApp controls the signed JSON and could send `allowed = 1 / "true" / "1" / "0x1"`
  — all true at the on-chain DAI verifier — to slip an unlimited-allowance signature past the guard.
  Every true-encoding is now flagged HIGH; `false`/`0` are not (no false positive).
- Security (check_action): `forbid_tools` matching now strips whitespace and normalizes case, so a
  forbidden tool name like `"send\n"` can no longer fail open while `allow_tools` failed closed.

## 0.5.3 — 2026-06-03
- Docs: recalibrated the "honest limits" section (static analysis, not a simulator; EVM-only safety;
  not yet field-proven) and added a validation note against real documented drainer techniques.

## 0.5.0–0.5.2 — 2026-06-03
- Security (inspect_typed_data): added Permit2 SignatureTransfer coverage
  (PermitTransferFrom / PermitBatchTransferFrom), flagging only an effectively-unlimited permitted
  amount to avoid crying wolf on the exact amounts legitimate apps use.
- Security (preflight): EIP-7702 account-delegation detection hardened to be case- and
  shape-insensitive (single-dict authorization, non-canonical field casing) — defense in depth.

## 0.4.0 — 2026-06-03
- Suite complete: all three guards — `preflight` (unsigned-tx drain decode), `inspect_typed_data`
  (EIP-712 permit-phishing), and `check_action` (allow/forbid + value/recipient policy) — are
  exported and exposed on the MCP surface (`preflight`, `inspect_signature`, `check_action`).

## 0.3.0 — 2026-06
- Added `inspect_typed_data`: catches permit-phishing in EIP-712 signatures (ERC-2612, Uniswap
  Permit2 PermitSingle/PermitBatch, DAI-style) before the agent signs.

## 0.2.x — 2026-06
- preflight hardening: unlimited/large approval, `increaseAllowance`, `setApprovalForAll`,
  ERC-20 `transferFrom` + ERC-721/1155 `safeTransferFrom`, on-chain `permit`, proxy
  `upgradeTo`/`upgradeToAndCall`, approvals hidden in `multicall` (all router variants + nested,
  depth-capped), large native value, opaque calldata, and will-revert via an injectable sim hook.

## 0.1.x — 2026-05/06
- Initial releases: non-custodial multi-chain wallet for AI agents (burner, balance, send, swap,
  bridge) with the first version of the `preflight` transaction-safety check. Keys generated and
  signed locally; no account, no custody, no signing backend.
