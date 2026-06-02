"""Red tests — remaining stress-test findings (2026-06-01 round 2): protocol + DX correctness."""
import pytest
from chain_signer import to_wei, create_wallet
from chain_signer.mcp_server import call_tool
from chain_signer.mcp_stdio import handle


def test_no_id_known_method_is_a_notification_no_response():
    # JSON-RPC: a request with no id is a notification -> MUST get no response, even for known methods
    assert handle({"jsonrpc": "2.0", "method": "ping"}) is None
    assert handle({"jsonrpc": "2.0", "method": "tools/list"}) is None


def test_create_wallet_tool_can_restore_from_key():
    w = create_wallet("evm")  # known address+key
    out = call_tool("create_wallet", {"chain": "evm", "private_key": w.private_key})
    assert out["address"] == w.address, "create_wallet tool must restore the SAME address from a key"


def test_to_wei_rejects_negative():
    with pytest.raises(ValueError):
        to_wei(-1)


def test_py_typed_marker_present():
    import importlib.resources as r
    assert (r.files("chain_signer") / "py.typed").is_file(), "ship a py.typed marker (PEP 561)"
