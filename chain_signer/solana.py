"""Solana transfers (non-custodial) via solders + Solana JSON-RPC.

The owning SolanaWallet signs with its own ed25519 key, locally. The signed transaction is
serialized (base64) and handed to an injectable `broadcast` (sendTransaction) so signing is
unit-testable with no network/funds. GREEN STEP fills this in.
"""
from .balance import _default_solana_rpc


def _get_blockhash(rpc) -> str:
    res = (rpc or _default_solana_rpc)("getLatestBlockhash", [{"commitment": "finalized"}])
    return res["value"]["blockhash"]


def send_solana(wallet, to, lamports, *, recent_blockhash=None, rpc=None, broadcast=None):
    """Sign + post a SOL transfer with the owner's key. Returns the tx signature."""
    import base64

    import base58
    from solders.hash import Hash
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import TransferParams, transfer
    from solders.transaction import Transaction

    kp = Keypair.from_bytes(base58.b58decode(wallet.private_key))
    ix = transfer(TransferParams(from_pubkey=kp.pubkey(), to_pubkey=Pubkey.from_string(str(to)), lamports=int(lamports)))
    blockhash = Hash.from_string(recent_blockhash or _get_blockhash(rpc))
    tx = Transaction.new_signed_with_payer([ix], kp.pubkey(), [kp], blockhash)
    tx_b64 = base64.b64encode(bytes(tx)).decode()
    signature = str(tx.signatures[0])
    if broadcast is not None:
        returned = broadcast(tx_b64)
        if returned:
            signature = returned
    return {"signature": signature, "from": str(kp.pubkey()), "to": str(to), "lamports": int(lamports)}
