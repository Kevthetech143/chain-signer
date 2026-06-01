# Security Policy

chain-signer is a tool your AI agent uses to hold and use a crypto wallet. Keys are involved,
so here is exactly how it behaves and what to trust.

## Non-custodial by design
- The wallet's private key is created and held by YOU (your process). We never transmit it,
  store it on any server, or have any way to see it. There is no chain-signer account or backend.
- All signing happens locally in your process via `eth_account`. We build and sign the
  transaction on your machine; only the already-signed transaction is broadcast.
- There is no remote service in the signing path. If our project disappeared tomorrow, your keys
  and funds would be unaffected — they were never ours.

## Key handling
- `burner()` / `create_wallet()` generate a key in memory and hand it to you on the returned
  wallet object. What you do with it is your responsibility.
- Do not log, print, or commit a private key. Treat `wallet.private_key` like a password.
- For storage at rest, use `export_encrypted(wallet, password)` — a standard encrypted keystore
  (Web3 Secret Storage / `eth_account`). Store that, not the plaintext key. Decrypt with
  `load_encrypted(keystore, password)`.

## Scope and intended use
- chain-signer is general-purpose, non-custodial wallet tooling for developers and AI agents.
- You are responsible for how you use it and for compliance with the laws that apply to you.
- It is not marketed for, or tailored to, any specific regulated activity.

## Reporting a vulnerability
Found a security issue? Please open a GitHub security advisory on the repository
(github.com/Kevthetech143/chain-signer → Security → Report a vulnerability), or open a private
issue. Do not post exploit details in a public issue before a fix is available. We aim to
acknowledge reports promptly and fix confirmed issues in a new release.

## Supported versions
The latest published version on PyPI receives fixes. Security fixes are released as a new version
(we never overwrite a published one).
