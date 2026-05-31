"""Non-custodial wallet.

The private key is generated or loaded LOCALLY and held by the owning agent. It must never
appear in repr/str, in public_info(), in logs, or in any serialized output. The owner can
access it (to sign) via the explicit `.private_key` property — that is the only path.

GREEN STEP fills these in. They raise NotImplementedError on purpose so the red tests fail.
"""

SUPPORTED_CHAINS = ("evm",)  # solana, bitcoin come in phase 1.5


class Wallet:
    def __init__(self, chain: str, private_key: str | None = None):
        raise NotImplementedError("green step")

    @property
    def address(self) -> str:
        raise NotImplementedError("green step")

    @property
    def private_key(self) -> str:
        raise NotImplementedError("green step")

    def public_info(self) -> dict:
        """Safe-to-share info. MUST NOT contain the private key."""
        raise NotImplementedError("green step")


def create_wallet(chain: str = "evm", private_key: str | None = None) -> Wallet:
    """Create a fresh non-custodial wallet, or load one from an existing private key.

    Same key -> same address (deterministic), so an agent fully owns and can restore its wallet.
    """
    raise NotImplementedError("green step")
