"""Regression: the MCP dispatch layer (call_tool) for the three safety tools must FAIL SAFE on
malformed/missing/wrong-type arguments an agent might pass — never crash, and never return a
silently-"safe" verdict on junk. Locks the verified behavior so a future refactor can't regress it.

- preflight / inspect_signature on junk → ok=False (an 'unparseable' flag), not ok=True.
- check_action on junk or a misconfigured policy → allowed=False (fail closed).
"""
import pytest
from chain_signer.mcp_server import call_tool

MALFORMED_TX = [None, {}, {"tx": 12345}, {"tx": "0xdeadbeef"}, {"tx": "garbage"}]
MALFORMED_TD = [{}, {"typed_data": "garbage"}, {"typed_data": 999}, {"typed_data": None}]
MALFORMED_ACTION = [None, {}, {"action": []}, {"action": {"tool": "send"}, "policy": "notadict"},
                    {"action": {"tool": "send"}, "policy": {"allow_tools": "send"}}]  # policy field wrong type


@pytest.mark.parametrize("args", MALFORMED_TX)
def test_preflight_dispatch_failsafe(args):
    r = call_tool("preflight", args)
    assert isinstance(r, dict)
    assert r.get("ok") is False  # junk is never silently safe


@pytest.mark.parametrize("args", MALFORMED_TD)
def test_inspect_signature_dispatch_failsafe(args):
    r = call_tool("inspect_signature", args)
    assert isinstance(r, dict)
    assert r.get("ok") is False


@pytest.mark.parametrize("args", MALFORMED_ACTION)
def test_check_action_dispatch_failsafe(args):
    r = call_tool("check_action", args)
    assert isinstance(r, dict)
    assert r.get("allowed") is False  # a policy gate must fail closed


def test_dispatch_does_not_crash_on_none_arguments():
    # None arguments at the dispatch boundary must be tolerated for every safety tool
    for name in ("preflight", "inspect_signature", "check_action"):
        assert isinstance(call_tool(name, None), dict)
