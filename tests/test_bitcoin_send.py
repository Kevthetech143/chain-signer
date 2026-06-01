"""Red tests — Bitcoin UTXO send (non-custodial). Fake unspent (offline) + injected broadcast: no funds.

bit's real signer produces the signed raw tx with the owner's key (genuine signing over a test UTXO).
"""
from bit.network.meta import Unspent
from bit.transaction import address_to_scriptpubkey

from chain_signer import create_wallet
from chain_signer.bitcoin import send_bitcoin


def _fake_unspent_for(wallet, sats=1_000_000):
    spk = address_to_scriptpubkey(wallet.address).hex()
    return Unspent(sats, 6, spk, "aa" * 32, 0)


def _broadcast():
    def b(raw):
        b.raw = raw
        return "f" * 64  # a txid
    b.raw = None
    return b


def test_send_bitcoin_builds_signed_tx_and_broadcasts():
    w = create_wallet("bitcoin", testnet=True)
    to = create_wallet("bitcoin", testnet=True).address
    bc = _broadcast()
    res = send_bitcoin(w, to, 0.001, unspents=[_fake_unspent_for(w)], broadcast=bc)
    assert res["from"] == w.address
    assert res["to"] == to
    assert res["raw"].startswith("0100000001"), f"not a signed v1 tx: {res['raw'][:12]}"
    bytes.fromhex(res["raw"])  # valid hex
    assert bc.raw == res["raw"], "broadcast did not receive the signed raw tx"
    assert res["txid"] == "f" * 64


def test_send_bitcoin_carries_amount():
    w = create_wallet("bitcoin", testnet=True)
    to = create_wallet("bitcoin", testnet=True).address
    res = send_bitcoin(w, to, 0.002, unspents=[_fake_unspent_for(w)], broadcast=lambda r: "tid")
    assert res["amount_btc"] == 0.002
