"""Red tests — sign + post a native transfer (non-custodial).

The broadcast is injected, so these are deterministic with NO network and NO funds.
The crown check: the signed transaction must recover to the OWNER's address — proof we
signed directly with the owner's own key.
"""
import pytest
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.tx import send

TO = "0x000000000000000000000000000000000000dEaD"


def _capture_broadcast():
    def broadcast(raw_hex):
        broadcast.raw = raw_hex
        broadcast.calls += 1
        return "0x" + "ab" * 32  # the network's tx hash
    broadcast.raw = None
    broadcast.calls = 0
    return broadcast


def _do_send(wallet, broadcast):
    return send(
        wallet, TO, 1000,
        chain="evm", nonce=0,
        max_fee_per_gas=30_000_000_000, max_priority_fee_per_gas=1_000_000_000,
        chain_id=80002, broadcast=broadcast,  # Polygon Amoy testnet
    )


def test_send_broadcasts_signed_tx_and_returns_the_network_hash():
    broadcast = _capture_broadcast()
    res = _do_send(create_wallet("evm"), broadcast)
    assert broadcast.calls == 1, "broadcast was not called exactly once"
    assert res["hash"] == "0x" + "ab" * 32, f"did not return the network hash: {res.get('hash')}"
    assert isinstance(broadcast.raw, str) and broadcast.raw.startswith("0x"), f"raw tx not 0x-hex: {broadcast.raw!r}"


def test_signed_transaction_recovers_to_the_owner_address():
    w = create_wallet("evm")
    broadcast = _capture_broadcast()
    _do_send(w, broadcast)
    sender = Account.recover_transaction(broadcast.raw)
    assert sender == w.address, f"signed tx recovered to {sender}, not owner {w.address}"


def test_send_targets_the_requested_recipient_and_value():
    res = _do_send(create_wallet("evm"), _capture_broadcast())
    assert res["to"].lower() == TO.lower(), f"wrong recipient: {res['to']}"
    assert res["value"] == 1000, f"wrong value: {res['value']}"


def test_result_never_contains_the_private_key():
    w = create_wallet("evm")
    res = _do_send(w, _capture_broadcast())
    assert w.private_key not in str(res), "private key leaked into the send result"


def test_send_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        send(
            create_wallet("evm"), TO, 1,
            chain="dogecoin", nonce=0,
            max_fee_per_gas=1, max_priority_fee_per_gas=1, chain_id=1,
            broadcast=_capture_broadcast(),
        )
