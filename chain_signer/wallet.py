"""Non-custodial wallet.

The private key is generated or loaded LOCALLY and held by the owning agent. It never
appears in repr/str, in public_info(), in logs, or in any serialized output. The owner can
access it (to sign) via the explicit `.private_key` property — that is the only path.
"""
from eth_account import Account

SUPPORTED_CHAINS = ("evm", "solana", "bitcoin")


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


class SolanaWallet:
    """Non-custodial Solana wallet (ed25519 via solders). Same key-secrecy rules as the EVM Wallet."""

    def __init__(self, private_key: str | None = None):
        import base58
        from solders.keypair import Keypair
        kp = Keypair.from_bytes(base58.b58decode(private_key)) if private_key else Keypair()
        self._private_key = base58.b58encode(bytes(kp)).decode()  # 64-byte secret, base58
        self._address = str(kp.pubkey())

    @property
    def chain(self) -> str:
        return "solana"

    @property
    def address(self) -> str:
        return self._address

    @property
    def private_key(self) -> str:
        return self._private_key

    def public_info(self) -> dict:
        return {"address": self._address, "chain": "solana"}

    def __repr__(self) -> str:
        return f"SolanaWallet(address={self._address!r})"

    __str__ = __repr__


class BitcoinWallet:
    """Non-custodial Bitcoin wallet (UTXO; via the `bit` library). Transfers only — Bitcoin has no apps."""

    def __init__(self, private_key: str | None = None, testnet: bool = False):
        from bit import Key, PrivateKeyTestnet
        cls = PrivateKeyTestnet if testnet else Key
        self._k = cls(private_key) if private_key else cls()
        self._testnet = testnet
        self._private_key = self._k.to_wif()
        self._address = self._k.address

    @property
    def chain(self) -> str:
        return "bitcoin"

    @property
    def address(self) -> str:
        return self._address

    @property
    def private_key(self) -> str:
        return self._private_key

    def public_info(self) -> dict:
        return {"address": self._address, "chain": "bitcoin"}

    def __repr__(self) -> str:
        return f"BitcoinWallet(address={self._address!r}, testnet={self._testnet})"

    __str__ = __repr__


def create_wallet(chain: str = "evm", private_key: str | None = None, *, testnet: bool = False):
    """Create a fresh non-custodial wallet, or load one from an existing private key.

    Dispatches by chain. Same key -> same address (deterministic), so an agent fully owns and can
    restore its wallet. `testnet` applies to Bitcoin (mainnet by default).
    """
    if chain == "evm":
        return Wallet("evm", private_key=private_key)
    if chain == "solana":
        return SolanaWallet(private_key=private_key)
    if chain == "bitcoin":
        return BitcoinWallet(private_key=private_key, testnet=testnet)
    raise ValueError(f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}")
