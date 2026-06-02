"""Red tests — fixes for the adversarial stress test (2026-06-02). A safety tool must NEVER crash
(fail-safe, not fail-open) and must cover the real drain calls."""
import pytest
from chain_signer.preflight import preflight

SP = "0x" + "11" * 20
VICTIM = "0x" + "ab" * 20


def codes(r): return {f["code"] for f in r["risk_flags"]}


def test_value_as_hex_string_does_not_crash():
    r = preflight({"to": "0x" + "44" * 20, "data": "0x", "value": "0x1bc16d674ec80000"}, max_value=10**18)
    assert isinstance(r, dict)  # no exception
    assert "large_native_value" in codes(r)  # 2 ETH > 1 ETH limit, correctly flagged


def test_malformed_calldata_does_not_crash():
    # non-hex word in a known selector's args must NOT raise — flag it instead
    r = preflight({"to": "0x" + "22" * 20, "data": "0x095ea7b3" + "z" * 128, "value": 0})
    assert isinstance(r, dict)
    assert "malformed_call" in codes(r)


def test_non_dict_input_does_not_crash():
    for bad in (None, [], "0xdead"):
        r = preflight(bad)
        assert isinstance(r, dict) and r["ok"] is False


def test_transferFrom_is_flagged():
    # 0x23b872dd transferFrom(from,to,amount) — the drain-execution call
    data = "0x23b872dd" + VICTIM[2:].rjust(64, "0") + SP[2:].rjust(64, "0") + format(10**30, "064x")
    r = preflight({"to": "0x" + "22" * 20, "data": data, "value": 0})
    assert "token_transfer_from" in codes(r) and r["ok"] is False


def test_proxy_upgrade_is_high():
    # upgradeTo(address) 0x3659cfe6 — repoints a proxy's logic; classic rug/compromise
    data = "0x3659cfe6" + ("0x" + "de" * 20)[2:].rjust(64, "0")
    r = preflight({"to": "0x" + "22" * 20, "data": data, "value": 0})
    assert "proxy_upgrade" in codes(r) and r["ok"] is False


def test_truncated_known_call_not_silently_clean():
    # approve selector with only the spender word (amount missing) must not pass as clean
    r = preflight({"to": "0x" + "22" * 20, "data": "0x095ea7b3" + SP[2:].rjust(64, "0"), "value": 0})
    assert "malformed_call" in codes(r)
