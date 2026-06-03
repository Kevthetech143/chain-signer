# Threat coverage — what the suite catches, and what it honestly doesn't

A security tool earns trust by being explicit about its limits. This maps known AI-agent
fund-drain vectors to our coverage. ✅ covered · 🟡 partial · ❌ not yet (honest gap). A guard,
not a guarantee — pair it with your wallet + identity stack.

## Transaction signing — `preflight(tx)`
| Vector | Coverage | Notes |
|---|---|---|
| Unlimited / large ERC-20 `approve` | ✅ | HIGH on unlimited, MED on large |
| `increaseAllowance` | ✅ | same thresholds |
| `setApprovalForAll(true)` (NFT operator) | ✅ | HIGH |
| ERC-20 `transferFrom` | ✅ | HIGH (drain-execution call) |
| ERC-721/1155 `safeTransferFrom` (NFT theft) | ✅ | HIGH |
| On-chain `permit()` call | ✅ | HIGH on unlimited |
| Proxy `upgradeTo` / `upgradeToAndCall` | ✅ | HIGH (logic swap) |
| Approval hidden in `multicall` (all 4 variants, nested) | ✅ | recurses, depth-capped |
| EIP-7702 account delegation ("wallet upgrade" drainer) | ✅ | HIGH; flags the delegate target |
| Large native value | ✅ | MED, against a caller `max_value` |
| Will-revert (wasted gas / unexpected) | 🟡 | needs an injected `sim` hook |
| Opaque / unknown calldata | ✅ | LOW (can't read intent) |
| Uniswap Universal Router `execute()` | ❌ | commands/inputs encoding; FP-prone — on real demand |
| Multicall3 `aggregate3`/`tryAggregate` | ❌ | executes in the contract's context, not the user's — not a direct user drain |
| Real balance-diff via on-chain simulation | 🟡 | hook is injectable; no built-in sim engine (avoids a heavy dep) |

## Off-chain signatures — `inspect_typed_data(td)`
| Vector | Coverage | Notes |
|---|---|---|
| ERC-2612 `permit` signature (unlimited) | ✅ | HIGH; the classic signature-phishing drain |
| Uniswap Permit2 `PermitSingle`/`PermitBatch` | ✅ | uint160-aware threshold |
| DAI-style `permit` (`allowed: true`) | ✅ | HIGH |
| Permit2 `PermitTransferFrom`/`PermitBatchTransferFrom` (SignatureTransfer) | ✅ | flags only UNLIMITED permitted amount (legit swaps use exact amounts → no false alarm) |
| Seaport order signatures (NFT listing phishing) | ❌ | FP-prone vs legit listings; needs offer/consideration value compare — on demand |

## Agent actions — `check_action(action, policy)`
| Vector | Coverage | Notes |
|---|---|---|
| Forbidden / non-allowlisted tool call | ✅ | case-insensitive; empty allowlist fails CLOSED |
| Over-limit native value | ✅ | `max_value_wei` |
| Recipient not on allowlist | ✅ | case-insensitive |

## Known honest limits (by design)
- Static decoding can't read intent it can't decode (opaque calldata → LOW, not a pass).
- Simulation evasion ("red-pill" contracts that behave in a sim then drain on-chain) — a reason we
  treat `sim` as advisory and still rely on calldata/signature decoding.
- We are a complement, not a replacement for: hardware-wallet confirmation, MPC custody, or an
  identity layer. The seatbelt, not the whole car.

_Last updated 2026-06-03 (v0.5.0). Gaps are tracked honestly; we close the ones with real demand
or a clean, low-false-positive rule — never ship a guard that cries wolf._
