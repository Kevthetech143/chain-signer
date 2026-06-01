# chain-signer — Pattern Catalog

Evidence-backed patterns this project reuses. Each earned its spot with 3+ shipped instances
(see docs/patterns/audit-2026-06-01.md). Every entry carries the trap that bit us so reuse
inherits the lesson. /patterns-reuse reads this file; classify a new feature against it before building.

Approved: 2026-06-01 (Kelvin — "approve all").

---

## 1. Injectable network seam
Problem: make every external call (HTTP / RPC / broadcast) substitutable so logic is unit-testable with zero network and zero funds.
Reference: chain_signer/balance.py:64
Canonical shape: the function takes an optional callable param defaulting to None (e.g. `fetch=None`, `rpc=None`, `broadcast=None`); inside, resolve `dep = dep or _default_dep`; the default does the real network call, tests pass a fake that returns canned data and/or captures the request.
Known trap: an injectable hook makes the call substitutable but does NOT validate the response — get_balance never checks Etherscan's `status` field, so an error payload raises an opaque error on `int()` (STATUS.md known-limitations). Validate the shape too.
Test contract: tests/test_solana_balance.py — inject the dep, assert the converted result AND that the right request was made.
Use when: any function touches an external network/RPC/HTTP service. Skip when: pure-compute, no I/O.

## 2. Chain-dispatch guard
Problem: route one public API across multiple chains/backends and reject unknown ones with a clear, consistent error.
Reference: chain_signer/wallet.py:118 (create_wallet)
Canonical shape: a module-level `SUPPORTED_CHAINS` tuple; the entry function branches `if chain == "<x>": return <x_impl>(…)` per chain; a final `raise ValueError(f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}")`.
Known trap: a chain added to `SUPPORTED_CHAINS` but NOT given a routing branch silently falls through to the wrong adapter — keep chain-specific classes single-chain; put routing in the dispatch function, not the class.
Test contract: tests/test_wallet.py::test_unsupported_chain_raises_value_error + per-chain create_wallet tests.
Use when: any multi-chain/multi-backend entry point. Skip when: single-backend code.

## 3. Sign-and-broadcast recipe (EVM)
Problem: build, locally sign with the owner's key, and optionally broadcast an EIP-1559 tx — non-custodial, broadcast injectable.
Reference: chain_signer/tx.py:54 (send)
Canonical shape: build the EIP-1559 dict (`type:2`, nonce/gas/fees/chainId); `signed = Account.sign_transaction(tx, wallet.private_key)` then `raw_hex = _to_0x_hex(signed.raw_transaction)`; `if broadcast is not None: returned = broadcast(raw_hex); if returned: tx_hash = returned`.
Known trap: the locally-computed tx hash EQUALS the network hash, so a returned hash does NOT prove the broadcast landed — a real mainnet send sat pending and a replacement mined reverted (status 0x0) before a clean send. Always confirm via the receipt (STATUS.md LIVE PROOF).
Test contract: tests/test_send.py::test_signed_transaction_recovers_to_the_owner_address (recover signer from raw).
Use when: any EVM state-changing tx. Skip when: non-EVM (Solana/Bitcoin use the same SHAPE, different libs — do not copy this exact code).

## 4. Key-secrecy wallet invariant
Problem: hold a private key the owner can use to sign, while guaranteeing it never leaks into representations, logs, or shared info.
Reference: chain_signer/wallet.py:22 (Wallet)
Canonical shape: store the secret as `self._private_key`; expose it only via a `.private_key` property used solely for signing; `public_info()` returns `{address, chain}` only; `__repr__`/`__str__` print address only, with `__str__ = __repr__`.
Known trap: the key still lives in the instance `__dict__`, so `vars()`/`pickle` would expose it — no redaction test yet (STATUS.md known-limitations). Add a redaction guard when hardening.
Test contract: tests/test_wallet.py::test_private_key_never_leaks_into_repr (+ solana/bitcoin equivalents).
Use when: any object holds a secret the owner must use but must not leak. Skip when: no secret to protect.
