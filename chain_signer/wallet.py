"""Non-custodial wallet.

The private key is generated or loaded LOCALLY and held by the owning agent. It never
appears in repr/str, in public_info(), in logs, or in any serialized output. The owner can
access it (to sign) via the explicit `.private_key` property — that is the only path.
"""
from eth_account import Account

SUPPORTED_CHAINS = ("evm",)  # solana, bitcoin come in phase 1.5


def _normalize_key(key: str | bytes) -> str:
    """Return a 0x-prefixed, lowercase, 64-hex-char private key string."""
    if isinstance(key, bytes):
        key = key.hex()
    key = str(key)
    if key.startswith(("0x", "0X")):
        key = key[2:]
    return "0x" + key.lower()


class Wallet:
    def __init__(self, chain: str, private_key: str | None = None):
        if chain not in SUPPORTED_CHAINS:
            raise ValueError(
                f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}"
            )
        self._chain = chain
        account = Account.from_key(private_key) if private_key else Account.create()
        # _private_key is the owner's secret. Never put it in repr/str/public_info/logs.
        self._private_key = _normalize_key(account.key)
        self._address = account.address  # EIP-55 checksummed

    @property
    def chain(self) -> str:
        return self._chain

    @property
    def address(self) -> str:
        return self._address

    @property
    def private_key(self) -> str:
        return self._private_key

    def public_info(self) -> dict:
        """Safe-to-share info. Never contains the private key."""
        return {"address": self._address, "chain": self._chain}

    def __repr__(self) -> str:
        return f"Wallet(chain={self._chain!r}, address={self._address!r})"

    __str__ = __repr__


def create_wallet(chain: str = "evm", private_key: str | None = None) -> Wallet:
    """Create a fresh non-custodial wallet, or load one from an existing private key.

    Same key -> same address (deterministic), so an agent fully owns and can restore its wallet.
    """
    return Wallet(chain, private_key=private_key)
