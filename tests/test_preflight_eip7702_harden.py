"""Adversarial-review hardening (2026-06-03) of the EIP-7702 detection: a guard shouldn't be
defeated by input shape/casing. Accept a single-dict authorization (not just a list) and match the
field name case/underscore-insensitively. (Real-world authorizations come from libs in standard
shape; this is defense-in-depth so a non-canonical shape can't slip a delegation past.)
"""
from chain_signer.preflight import preflight

DELEGATE = "0x" + "de" * 20


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_single_dict_authorization_is_flagged():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0,
          "authorizationList": {"chainId": 1, "address": DELEGATE, "nonce": 0}}  # single dict, not a list
    assert "eip7702_delegation" in _codes(preflight(tx))


def test_uppercase_field_name_is_flagged():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0,
          "AUTHORIZATIONLIST": [{"chainId": 1, "address": DELEGATE, "nonce": 0}]}
    assert "eip7702_delegation" in _codes(preflight(tx))


def test_snake_case_still_works():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0,
          "authorization_list": [{"chainId": 1, "address": DELEGATE, "nonce": 0}]}
    assert "eip7702_delegation" in _codes(preflight(tx))


def test_non_dict_auth_entries_do_not_crash():
    tx = {"to": "0x" + "33" * 20, "data": "0x", "value": 0,
          "authorizationList": ["junk", {"address": DELEGATE}]}
    r = preflight(tx)   # must not raise; still flags (an authorization is present)
    assert isinstance(r, dict) and "eip7702_delegation" in _codes(r)


def test_no_authorization_still_not_flagged():
    assert "eip7702_delegation" not in _codes(preflight({"to": "0x" + "33" * 20, "data": "0x", "value": 0}))
