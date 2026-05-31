"""Red tests — sign + post a contract/app call (non-custodial).

Deterministic: broadcast injected, no network/funds. Pins that we encode the right function
selector + args, and that the signed call recovers to the OWNER (proof of direct signing).
"""
import pytest
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.tx import call_contract

CONTRACT = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC.e on Polygon
RECIPIENT = "0x000000000000000000000000000000000000dEaD"


def _capture_broadcast():
    def broadcast(raw_hex):
        broadcast.raw = raw_hex
        broadcast.calls += 1
        return "0x" + "cd" * 32
    broadcast.raw = None
    broadcast.calls = 0
    return broadcast


def _do_call(wallet, broadcast):
    return call_contract(
        wallet, CONTRACT, "transfer(address,uint256)", [RECIPIENT, 1000],
        chain="evm", nonce=0,
        max_fee_per_gas=30_000_000_000, max_priority_fee_per_gas=1_000_000_000,
        chain_id=80002, broadcast=broadcast,
    )


def test_encodes_the_correct_function_selector_and_recipient():
    res = _do_call(create_wallet("evm"), _capture_broadcast())
    # ERC-20 transfer(address,uint256) selector is 0xa9059cbb
    assert res["data"].startswith("0xa9059cbb"), f"wrong function selector: {res['data'][:10]}"
    assert RECIPIENT.lower()[2:] in res["data"].lower(), "recipient address not encoded in call data"


def test_signed_call_recovers_to_the_owner_address():
    w = create_wallet("evm")
    broadcast = _capture_broadcast()
    _do_call(w, broadcast)
    sender = Account.recover_transaction(broadcast.raw)
    assert sender == w.address, f"signed call recovered to {sender}, not owner {w.address}"


def test_call_targets_the_contract_address():
    res = _do_call(create_wallet("evm"), _capture_broadcast())
    assert res["to"].lower() == CONTRACT.lower(), f"wrong contract target: {res['to']}"


def test_call_result_never_contains_the_private_key():
    w = create_wallet("evm")
    res = _do_call(w, _capture_broadcast())
    assert w.private_key not in str(res), "private key leaked into the call result"


def test_call_unsupported_chain_raises_value_error():
    with pytest.raises(ValueError):
        call_contract(
            create_wallet("evm"), CONTRACT, "transfer(address,uint256)", [RECIPIENT, 1],
            chain="dogecoin", nonce=0,
            max_fee_per_gas=1, max_priority_fee_per_gas=1, chain_id=1,
            broadcast=_capture_broadcast(),
        )
