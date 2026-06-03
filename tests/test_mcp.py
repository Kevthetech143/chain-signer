"""Red tests — the tool surface any AI calls (list_tools / call_tool).

Deterministic: fetch + broadcast injected. Pins that all five functions are exposed and
routed correctly, and that signing tools never echo the private key back.
"""
import re

import pytest

from chain_signer.mcp_server import list_tools, call_tool

EVM_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
EVM_PRIVATE_KEY = re.compile(r"^0x[0-9a-fA-F]{64}$")
TO = "0x000000000000000000000000000000000000dEaD"


def _broadcast():
    def b(raw):
        b.raw = raw
        return "0x" + "11" * 32
    b.raw = None
    return b


def _balance_fetch(result):
    def fetch(url):
        fetch.url = url
        return {"status": "1", "result": result}
    fetch.url = None
    return fetch


def test_list_tools_exposes_all_functions():
    names = {t["name"] for t in list_tools()}
    assert names == {"create_wallet", "get_balance", "send", "call_contract", "swap", "bridge",
                     "preflight", "inspect_signature"}, f"exposed: {names}"


def test_create_wallet_tool_returns_address_and_key():
    res = call_tool("create_wallet", {"chain": "evm"})
    assert EVM_ADDRESS.match(res["address"]), f"bad address: {res.get('address')}"
    assert EVM_PRIVATE_KEY.match(res["private_key"]), "create_wallet must return the key to its owner once"


def test_get_balance_tool_routes_and_converts():
    fetch = _balance_fetch("9854633000000000000")
    res = call_tool("get_balance", {"address": "0x01F5404f0FFCEFBA097817cC3765556240db46aD"}, fetch=fetch)
    assert res["balance"] == pytest.approx(9.854633), f"balance not converted: {res}"


def test_send_tool_signs_and_returns_hash_without_leaking_key():
    made = call_tool("create_wallet", {"chain": "evm"})
    broadcast = _broadcast()
    res = call_tool("send", {
        "private_key": made["private_key"], "to": TO, "value_wei": 1000,
        "nonce": 0, "max_fee_per_gas": 30_000_000_000, "max_priority_fee_per_gas": 1_000_000_000,
        "chain_id": 80002,
    }, broadcast=broadcast)
    assert res["hash"] == "0x" + "11" * 32, f"did not return network hash: {res.get('hash')}"
    assert made["private_key"] not in str(res), "send tool result leaked the private key"


def test_unknown_tool_raises_value_error():
    with pytest.raises(ValueError):
        call_tool("teleport", {})
