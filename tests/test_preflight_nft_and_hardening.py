"""Adversarial-review fixes (2026-06-02): NFT safeTransferFrom drains were treated as harmless
opaque calls; float('inf') value crashed the gate; unknown selectors hidden in a multicall
weren't even surfaced as opaque. All three found by an independent bypass hunt.
"""
from eth_abi import encode
from chain_signer.preflight import preflight

FROM = "0x" + "ab" * 20
TO = "0x" + "cd" * 20
NFT = "0x" + "33" * 20


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _sev(r, code):
    return next(f["severity"] for f in r["risk_flags"] if f["code"] == code)


def test_erc721_safe_transfer_from_is_high():
    # safeTransferFrom(address,address,uint256) = 0x42842e0e
    data = "0x42842e0e" + FROM[2:].rjust(64, "0") + TO[2:].rjust(64, "0") + format(12345, "064x")
    r = preflight({"to": NFT, "data": data, "value": 0})
    assert "token_transfer_from" in _codes(r)
    assert _sev(r, "token_transfer_from") == "HIGH"
    assert r["ok"] is False


def test_erc1155_safe_transfer_from_is_high():
    # safeTransferFrom(address,address,uint256,uint256,bytes) = 0xf242432a
    data = "0xf242432a" + FROM[2:].rjust(64, "0") + TO[2:].rjust(64, "0") + format(1, "064x") * 2 + "00" * 32
    r = preflight({"to": NFT, "data": data, "value": 0})
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_nft_drain_hidden_in_multicall_is_high():
    inner = bytes.fromhex("42842e0e" + FROM[2:].rjust(64, "0") + TO[2:].rjust(64, "0") + format(7, "064x"))
    data = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight({"to": NFT, "data": data, "value": 0})
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_infinite_value_does_not_crash():
    # must FAIL SAFE — return a report, never raise
    r = preflight({"to": TO, "data": "0x", "value": float("inf")})
    assert isinstance(r, dict) and "risk_flags" in r
    assert "unreadable_value" in _codes(r)


def test_unknown_selector_inside_multicall_surfaced():
    inner = bytes.fromhex("deadbeef" + "11" * 40)
    data = "0xac9650d8" + encode(["bytes[]"], [[inner]]).hex()
    r = preflight({"to": NFT, "data": data, "value": 0})
    assert "opaque_calldata" in _codes(r)
