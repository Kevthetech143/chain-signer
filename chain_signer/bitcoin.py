"""Bitcoin transfers (non-custodial, UTXO) via the `bit` library.

The owning BitcoinWallet signs with its own key, locally (offline given the unspents); the signed
raw tx is handed to an injectable `broadcast` so it's unit-testable with no network/funds.
NO contracts/swaps — Bitcoin isn't an app platform. GREEN STEP fills this in.
"""


def send_bitcoin(wallet, to, amount_btc, *, unspents=None, fee=None, broadcast=None):
    """Build + sign a BTC transfer and broadcast it. Returns the txid."""
    key = wallet._k  # the underlying bit Key / PrivateKeyTestnet
    outputs = [(str(to), amount_btc, "btc")]
    kwargs = {"unspents": unspents}
    if fee is not None:
        kwargs["fee"] = fee
    raw = key.create_transaction(outputs, **kwargs)  # signed raw tx hex (offline if unspents given)
    txid = broadcast(raw) if broadcast is not None else None
    return {"raw": raw, "txid": txid, "from": wallet.address, "to": str(to), "amount_btc": amount_btc}
