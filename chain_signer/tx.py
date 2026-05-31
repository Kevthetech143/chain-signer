"""Build, sign, and post transactions (non-custodial).

The owning Wallet signs with its OWN key, locally. The signed transaction is handed to an
injectable `broadcast` function (so signing is unit-testable with no network/funds). The
private key is never logged or returned.
"""
from eth_account import Account

SUPPORTED_CHAINS = ("evm",)


def _addr(target) -> str:
    return str(getattr(target, "address", target))


def _to_0x_hex(value) -> str:
    h = value.hex() if hasattr(value, "hex") else str(value)
    return h if h.startswith("0x") else "0x" + h


def send(
    wallet,
    to,
    value_wei,
    *,
    chain="evm",
    nonce,
    max_fee_per_gas,
    max_priority_fee_per_gas,
    gas=21000,
    chain_id=137,
    broadcast=None,
):
    """Sign a native-coin transfer and broadcast it. Returns a result dict with the tx hash."""
    if chain not in SUPPORTED_CHAINS:
        raise ValueError(
            f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}"
        )
    tx = {
        "to": to,
        "value": int(value_wei),
        "nonce": int(nonce),
        "gas": int(gas),
        "maxFeePerGas": int(max_fee_per_gas),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas),
        "chainId": int(chain_id),
        "type": 2,  # EIP-1559
    }
    signed = Account.sign_transaction(tx, wallet.private_key)
    raw_hex = _to_0x_hex(getattr(signed, "raw_transaction", None) or signed.rawTransaction)
    tx_hash = _to_0x_hex(getattr(signed, "hash", None) or signed.hash)
    if broadcast is not None:
        returned = broadcast(raw_hex)
        if returned:
            tx_hash = returned
    return {
        "hash": tx_hash,
        "from": _addr(wallet),
        "to": to,
        "value": int(value_wei),
        "raw": raw_hex,
    }
