"""EIP-7702 account-delegation drainers (live 2025/2026) — a real, current vector that bypasses
approve()-based detection. The signer authorizes delegating their EOA to a contract (a type-0x04
'set code' tx carries an authorizationList); the delegate can then move funds with no further input.
Attackers disguise it as a 'wallet upgrade' / 'AI assistant authorization'. preflight must flag any
tx that carries an EIP-7702 authorization.
"""
from chain_signer.preflight import preflight

DELEGATE = "0x" + "de" * 20


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_eip7702_authorization_list_is_high():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0,
          "authorizationList": [{"chainId": 1, "address": DELEGATE, "nonce": 0}]}
    r = preflight(tx)
    assert "eip7702_delegation" in _codes(r)
    assert r["ok"] is False


def test_eip7702_snake_case_field_also_caught():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0,
          "authorization_list": [{"chainId": 1, "address": DELEGATE, "nonce": 0}]}
    assert "eip7702_delegation" in _codes(preflight(tx))


def test_normal_tx_without_authorization_not_flagged():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0}
    assert "eip7702_delegation" not in _codes(preflight(tx))
