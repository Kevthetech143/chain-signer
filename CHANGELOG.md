# Changelog

All notable changes to chain-signer. Newest first. Security fixes are released as a new version —
published versions are never overwritten. Dates are UTC.

## 0.5.15 — 2026-06-07
- Security (preflight + inspect_typed_data): the HIGH "unlimited approval" net was 2**255, so an
  effectively-infinite approval BELOW that — e.g. 2**200 (~1.6e60), astronomically beyond any real
  ERC-20's total supply (largest are ~1e33 base units) — only WARNED (MED `large_approval`) with
  ok=True, escaping the `assert_safe` hard-stop. A drainer could pick a sub-2**255 value to dodge the
  block while still draining the token. Tightened `_UNLIMITED_THRESHOLD` to 1e40 — ~7 orders of
  magnitude above any real token supply (no false positive: 1e33 SHIB-scale stays MED) and well below
  every sub-max evasion. Same evasion CLASS as the v0.5.9 Permit2 uint160 "infinite below the ERC-20
  threshold" fix; applies to ERC-20 approve, on-chain permit, and the ERC-2612 permit signature path
  (shared constant). Red test (2**200 → HIGH) + full suite green (267).

## 0.5.14 — 2026-06-07
- Security (inspect_typed_data): a DAI-style `permit` (allowed=true) carrying a DECOY `value` key
  slipped past the guard. DAI detection only ran when `value` was ABSENT (`"allowed" in message and
  "value" not in message`), so a hostile dApp could add `value: 0` to dodge it — EIP-712 hashes only
  the fields declared in `types` (the DAI 5-field type, no `value`), so the wallet ignores the decoy
  key and still signs allowed=true (unlimited on-chain) while the guard waved it through (fail-OPEN).
  DAI detection now keys off the PRESENCE of `allowed` and the ERC-2612 value check runs independently
  — neither path can be evaded by adding/omitting the other's field. Same evasion class as 0.5.4.

## 0.5.13 — 2026-06-07
- Distribution (MCP surface): the `tools/list` introspection led with the WALLET tools
  (create_wallet/get_balance/send/...) and put the three security guards LAST — so a directory
  (Glama) or agent runtime reading the tool order saw a wallet-first server, contradicting the
  security wedge every other surface (README/PyPI/registry) leads with. Reordered `TOOL_SPECS` so
  preflight/inspect_signature/check_action come FIRST; wallet/exec tools follow. Presentation-only
  (dispatch is by name; zero behavior change) + a regression test locking the wedge to the front of
  the surface (265). Found by exercising the published-style artifact exactly as Glama does
  (initialize + tools/list over the stdio server).

## 0.5.12 — 2026-06-06
- Security (check_action): the `allow_recipients` whitelist failed OPEN and could crash. It only ran
  when `to` was present (`if allow_recipients and "to" in args`), so a value-bearing action that
  OMITTED `to` was ALLOWED — defeating the whole point of a recipient allow-list. And a non-string
  `to` (int/list) raised AttributeError via `(args.get("to") or "").lower()`, breaking the never-raises
  contract. Now fails CLOSED like `allow_tools`: a missing/unreadable `to` on a native-value transfer
  DENYs (`recipient_not_allowed`); a pure non-value action with no `to` is not flagged (non-noisy).

## 0.5.11 — 2026-06-06
- Security (inspect_typed_data): flag Seaport marketplace order signatures (primaryType
  `OrderComponents`) that give the offered asset away for ZERO/empty consideration — the NFT
  signature-phishing drain (off-chain sibling of setApprovalForAll). Conservative by design: normal-
  priced listings and buy orders are not flagged, only unambiguous zero-consideration giveaways.

## 0.5.10 — 2026-06-06
- Security (preflight): flag the on-chain Permit2 `permit()` entrypoint (single + batch). 0.5.9 caught
  Permit2 `approve()` but not `permit()`, which writes the identical (spender → unlimited uint160
  allowance) state — so an attacker could swap `approve` for `permit` and bypass the guard. The amount
  sits inside a tuple/tuple-array, so this uses real ABI decoding; batch flags if ANY entry is unlimited.

## 0.5.9 — 2026-06-06
- Security (preflight): detect the on-chain Permit2 surface — `approve()` (0x87517c45) and the
  `transferFrom()` drain-pull (0x36c78516). These flow through preflight as plain txs but were unknown
  selectors, so an unlimited Permit2 allowance was waved through. Permit2 uses uint160 amounts, so
  "infinite" is below the ERC-20 threshold — added a uint160-scaled unlimited check.

## 0.5.8 — 2026-06-04
- Security (check_action dispatch): a valid action with a malformed (non-dict, non-None) policy was
  coerced to an empty policy and ALLOWED — a fail-OPEN. A non-None non-dict policy now DENYs
  (`unparseable_policy`), matching the module's fail-closed contract. policy=None remains the
  documented no-policy default.

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
