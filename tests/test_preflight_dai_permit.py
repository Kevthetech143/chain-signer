"""Adversarial angle (2026-06-08): preflight covers the ON-CHAIN ERC-2612 permit (0xd505accf) and the
sig-inspector covers the SIGNED DAI-style permit (allowed=true), but NOT the ON-CHAIN DAI permit tx.
DAI's permit has a different selector and shape: permit(holder, spender, nonce, expiry, bool allowed,
v, r, s) = 0x8fcbaf0c — there is NO amount; `allowed=true` sets an effectively-unlimited allowance.
So a drainer who gets a DAI permit signed and submits it on-chain (or asks the agent to sign the permit
TX directly) granted attacker an unlimited allowance and flowed through preflight as a single opaque LOW
call: ok=True, assert_safe PASSED (empirically confirmed fail-OPEN).

Same evasion CLASS as the on-chain Permit2 permit gap and the Universal Router gap (v0.5.21): a covered
approval shape (DAI permit — already caught on the signed side) reachable through an uncovered on-chain
entrypoint. Fix: decode 0x8fcbaf0c and flag unlimited_approval/HIGH when allowed=true. Non-noisy: a DAI
permit with allowed=false is a REVOKE — must stay clean.
"""
from chain_signer.preflight import preflight, assert_safe
import pytest

HOLDER = "0x" + "11" * 20
ATTACKER = "0x" + "ee" * 20
TOKEN = "0x" + "33" * 20   # DAI


def _dai_permit(spender, allowed):
    # permit(address holder, address spender, uint256 nonce, uint256 expiry, bool allowed, u8 v, b32 r, b32 s)
    words = [
        HOLDER[2:].rjust(64, "0"),
        spender[2:].rjust(64, "0"),
        format(0, "064x"),               # nonce
        format(2 ** 48, "064x"),         # expiry
        format(1 if allowed else 0, "064x"),
        format(27, "064x"),              # v
        "00" * 32,                       # r
        "00" * 32,                       # s
    ]
    return "0x8fcbaf0c" + "".join(words)


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def test_dai_permit_allowed_true_is_unlimited_high():
    r = preflight({"to": TOKEN, "data": _dai_permit(ATTACKER, True), "value": 0})
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_dai_permit_allowed_true_hard_stops():
    with pytest.raises(ValueError):
        assert_safe({"to": TOKEN, "data": _dai_permit(ATTACKER, True), "value": 0})


def test_dai_permit_allowed_false_is_revoke_not_flagged():
    # allowed=false REVOKES the allowance — the opposite of dangerous; must stay clean.
    r = preflight({"to": TOKEN, "data": _dai_permit(ATTACKER, False), "value": 0})
    assert "unlimited_approval" not in _codes(r)
    assert r["ok"] is True


def test_dai_permit_wrapped_in_execute_is_caught():
    # smart-account routing: execute(token, 0, daiPermit(attacker, allowed=true)) must still flag.
    from eth_abi import encode
    inner = bytes.fromhex(_dai_permit(ATTACKER, True)[2:])
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"], [TOKEN, 0, inner]).hex()
    r = preflight({"to": "0x" + "44" * 20, "data": data, "value": 0})
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_dai_permit_malformed_does_not_crash():
    bad = "0x8fcbaf0c" + "00" * 4
    r = preflight({"to": TOKEN, "data": bad, "value": 0})
    assert isinstance(r, dict) and "risk_flags" in r
