"""Red tests — Solana SOL transfer (non-custodial). broadcast injected: deterministic, no funds.

Crown check: the serialized signed tx VERIFIES (signed by the owner's ed25519 key).
"""
import base64

import base58

from chain_signer import create_wallet
from chain_signer.solana import send_solana

TO = "So11111111111111111111111111111111111111112"  # valid 32-byte base58 pubkey
BLOCKHASH = base58.b58encode(bytes(32)).decode()  # valid 32-byte hash (all-zero) for signing


def _broadcast():
    def b(tx_b64):
        b.sent = tx_b64
        return "5" + "1" * 87  # a network signature string
    b.sent = None
    return b


def test_send_solana_builds_signs_and_broadcasts():
    w = create_wallet("solana")
    bc = _broadcast()
    res = send_solana(w, TO, 1_000_000, recent_blockhash=BLOCKHASH, broadcast=bc)
    assert res["from"] == w.address
    assert res["to"] == TO
    assert res["lamports"] == 1_000_000
    assert bc.sent is not None, "broadcast was not called"
    base64.b64decode(bc.sent)  # serialized tx is valid base64


def test_send_solana_returns_the_network_signature():
    w = create_wallet("solana")
    bc = _broadcast()
    res = send_solana(w, TO, 1, recent_blockhash=BLOCKHASH, broadcast=bc)
    assert res["signature"] == "5" + "1" * 87, f"did not return network signature: {res['signature']}"


def test_signed_solana_tx_verifies_as_owner_signed():
    from solders.transaction import Transaction
    w = create_wallet("solana")
    bc = _broadcast()
    send_solana(w, TO, 1_000_000, recent_blockhash=BLOCKHASH, broadcast=bc)
    tx = Transaction.from_bytes(base64.b64decode(bc.sent))
    tx.verify()  # raises if the signature is invalid -> proves the owner's key signed it
