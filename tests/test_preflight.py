"""Red tests — transaction preflight safety: decode + flag a dangerous EVM tx BEFORE signing.

Unit 1: unlimited/large ERC-20 approval — the classic drain vector. preflight(tx) decodes the
calldata and returns risk_flags; an approve() for (near) uint256-max is HIGH and report.ok is False.
"""
from chain_signer.preflight import preflight

SPENDER = "0x" + "11" * 20
MAXU = (1 << 256) - 1


def _approve(amount):
    # ERC-20 approve(address,uint256): selector 0x095ea7b3
    return {"to": "0x" + "22" * 20,
            "data": "0x095ea7b3" + SPENDER[2:].rjust(64, "0") + format(amount, "064x"),
            "value": 0}


def _codes(report):
    return {f["code"] for f in report["risk_flags"]}


def test_decodes_the_approve_call():
    r = preflight(_approve(100))
    assert r["decoded"]["function"] == "approve"
    assert r["decoded"]["args"][0].lower() == SPENDER.lower()
    assert r["decoded"]["args"][1] == 100


def test_unlimited_approval_is_high_and_blocks():
    r = preflight(_approve(MAXU))
    assert "unlimited_approval" in _codes(r)
    flag = next(f for f in r["risk_flags"] if f["code"] == "unlimited_approval")
    assert flag["severity"] == "HIGH"
    assert r["ok"] is False, "a HIGH flag must make report.ok False"


def test_finite_approval_not_flagged_unlimited():
    r = preflight(_approve(100 * 10**6))  # 100 USDC, normal
    assert "unlimited_approval" not in _codes(r)
    assert r["ok"] is True
