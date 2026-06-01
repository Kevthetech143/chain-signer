# Customer #1 (Kelvin) V1 feedback — 2026-06-01

Ran the wheel install + one-liner. WORKS. Fresh wallet in <1s. Verdict: "V1 ships."
Flags:
1. private_key is a plain attribute — README must warn: never log/print/write to a brain file. (SECURITY DOC)
2. No sign_message / sign_transaction method on Wallet; signing routed via module helpers (send_ether).
   Differs from web3.py Account idiom — needs a doc note AND a sign_message helper is worth adding (real flows: auth/SIWE).
3. Cosmetic pip warning: the `chain-signer` script dir not on PATH. Note for users.
Actions: README key-safety + signing-idiom + PATH note (this cycle); sign_message helper = T11 fast-follow (TDD).
