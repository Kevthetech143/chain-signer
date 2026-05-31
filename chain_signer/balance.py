"""Read on-chain balances from the LIVE chain (read-only, non-custodial).

Uses the Etherscan v2 API (authoritative indexer) — never a free public RPC, which can
return false zeros. The `fetch` dependency is injectable so the logic is unit-testable
without a network call. GREEN STEP fills this in.
"""
SUPPORTED_CHAINS = ("evm",)
CHAIN_IDS = {"evm": 137}  # Polygon mainnet


def get_balance(target, token=None, *, chain="evm", decimals=18, fetch=None):
    """Return the balance of `target` (a Wallet or 0x-address) in human units.

    token=None reads the native coin (POL); a token contract address reads that ERC-20.
    """
    raise NotImplementedError("green step")
