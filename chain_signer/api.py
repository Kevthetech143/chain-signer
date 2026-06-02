"""V1 developer-facing facade — think in ETH, send in one call.

Thin layer over the unit-tested engine: create_wallet (wallet.py) + send_live (live.py).
Builders pass ether amounts; we convert to integer wei exactly and let send_live fetch
nonce/gas and broadcast. Non-custodial throughout — the agent's key never leaves send().
"""
from decimal import Decimal

from .live import DEFAULT_CHAIN_ID, send_live
from .wallet import create_wallet

WEI_PER_ETHER = 10**18


def burner(chain="evm", *, testnet=False):
    """Make a fresh throwaway wallet for one task. The agent holds the key; discard when done.

    Same call as create_wallet() with no key — named for the burner-per-task pattern.
    """
    return create_wallet(chain, testnet=testnet)


def restore(private_key, chain="evm", *, testnet=False):
    """Reload a wallet from its exported private key. Same key -> same address (deterministic)."""
    return create_wallet(chain, private_key=private_key, testnet=testnet)


def to_wei(amount_ether) -> int:
    """Exact ether -> integer wei. Accepts int, float, str, or Decimal without float drift."""
    return int(Decimal(str(amount_ether)) * WEI_PER_ETHER)


def sign_message(wallet, text: str) -> str:
    """Sign a plain-text message with the wallet's key (EIP-191 personal_sign).

    Returns the 0x signature hex. Recoverable via eth_account Account.recover_message.
    For auth / sign-in-with-ethereum style flows. EVM wallets only.
    """
    from eth_account import Account
    from eth_account.messages import encode_defunct
    signed = Account.sign_message(encode_defunct(text=text), private_key=wallet.private_key)
    return signed.signature.to_0x_hex()


def sign_typed_data(wallet, domain: dict, types: dict, message: dict) -> str:
    """Sign EIP-712 typed structured data with the wallet's key (the agent-payments format).

    Used by x402 / EIP-3009 style flows where an agent authorizes a payment by signing typed data
    rather than plain text. Returns the 0x signature hex; recover via eth_account encode_typed_data +
    Account.recover_message. EVM wallets only. Non-custodial: key used transiently, never stored.
    """
    from eth_account import Account
    signed = Account.sign_typed_data(wallet.private_key, domain_data=domain,
                                     message_types=types, message_data=message)
    return signed.signature.to_0x_hex()


def sign_x402_payment(wallet, *, token, to, value, valid_before, valid_after=0,
                      nonce=None, chain_id, token_name="USD Coin", token_version="2") -> dict:
    """Build + sign an x402 payment authorization (EIP-3009 TransferWithAuthorization) in one call.

    Returns the header-ready payload {"signature", "authorization"} an agent puts in the x402
    payment header. The agent signs locally with its own key — non-custodial, no password prompt.

    token: the stablecoin contract (USDC/EURC). value: amount in base units (int). valid_before:
    unix expiry. nonce: random 32-byte hex; generated if omitted. token_name/token_version must match
    the token contract's EIP-712 domain (read its name()/version(); USDC is often "USD Coin"/"2").
    Spec: coinbase/x402 specs/schemes/exact/scheme_exact_evm.md.
    """
    import os
    nonce_bytes = os.urandom(32) if nonce is None else bytes.fromhex(str(nonce)[2:] if str(nonce).startswith("0x") else str(nonce))
    if len(nonce_bytes) != 32:
        raise ValueError("x402 nonce must be exactly 32 bytes (EIP-3009 bytes32); got "
                         f"{len(nonce_bytes)} bytes")
    value = int(value)  # coerce once so the signed amount and the advertised amount can never diverge
    domain = {"name": token_name, "version": token_version, "chainId": int(chain_id), "verifyingContract": token}
    types = {"TransferWithAuthorization": [
        {"name": "from", "type": "address"}, {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"}, {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"}, {"name": "nonce", "type": "bytes32"}]}
    message = {"from": wallet.address, "to": to, "value": int(value),
               "validAfter": int(valid_after), "validBefore": int(valid_before), "nonce": nonce_bytes}
    signature = sign_typed_data(wallet, domain, types, message)
    return {
        "signature": signature,
        "authorization": {
            "from": wallet.address, "to": to, "value": str(value),
            "validAfter": int(valid_after), "validBefore": int(valid_before),
            "nonce": "0x" + nonce_bytes.hex(),
        },
    }


def export_encrypted(wallet, password: str) -> dict:
    """Encrypt the wallet's key into a standard keystore dict (eth_account / Web3 Secret Storage).

    Store THIS at rest instead of the plaintext key. Decrypt later with load_encrypted + the password.
    EVM wallets only.
    """
    from eth_account import Account
    return Account.encrypt(wallet.private_key, password)


def load_encrypted(keystore: dict, password: str):
    """Decrypt a keystore dict (from export_encrypted) back into a Wallet. Wrong password raises."""
    from eth_account import Account
    key = Account.decrypt(keystore, password)
    return create_wallet("evm", private_key=key.hex())


def send_ether(wallet, to, amount_ether, *, chain="evm", chain_id=DEFAULT_CHAIN_ID, fetch=None):
    """One-call send: convert ether->wei, fetch nonce+gas, sign with the owner's key, broadcast.

    Returns the send_live result dict ({"hash", "raw", ...}). RPC is injectable via `fetch`.
    """
    return send_live(wallet, to, to_wei(amount_ether), chain=chain, chain_id=chain_id, fetch=fetch)
