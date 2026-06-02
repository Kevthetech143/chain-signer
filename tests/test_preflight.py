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


# --- unit 2: setApprovalForAll(true) ---
def _set_approval_for_all(approved):
    word = "1" if approved else "0"
    return {"to": "0x" + "33" * 20,
            "data": "0xa22cb465" + SPENDER[2:].rjust(64, "0") + word.rjust(64, "0"), "value": 0}


def test_set_approval_for_all_true_is_high():
    r = preflight(_set_approval_for_all(True))
    assert "approval_for_all" in _codes(r) and r["ok"] is False


def test_set_approval_for_all_false_is_fine():
    r = preflight(_set_approval_for_all(False))
    assert "approval_for_all" not in _codes(r) and r["ok"] is True


# --- unit 3: native value over threshold ---
def test_large_native_value_flagged_med():
    r = preflight({"to": "0x" + "44" * 20, "data": "0x", "value": 5 * 10**18}, max_value=10**18)
    codes = _codes(r)
    assert "large_native_value" in codes
    assert next(f for f in r["risk_flags"] if f["code"] == "large_native_value")["severity"] == "MED"


def test_small_native_value_not_flagged():
    r = preflight({"to": "0x" + "44" * 20, "data": "0x", "value": 1000}, max_value=10**18)
    assert "large_native_value" not in _codes(r)


# --- unit 4: opaque calldata to a contract ---
def test_opaque_calldata_is_low():
    r = preflight({"to": "0x" + "55" * 20, "data": "0xdeadbeef" + "00" * 40, "value": 0})
    assert "opaque_calldata" in _codes(r)
    assert next(f for f in r["risk_flags"] if f["code"] == "opaque_calldata")["severity"] == "LOW"


def test_plain_transfer_no_data_not_opaque():
    r = preflight({"to": "0x" + "44" * 20, "data": "0x", "value": 0})
    assert "opaque_calldata" not in _codes(r)


# --- unit 5: will-revert via injectable sim ---
def test_sim_revert_is_high():
    r = preflight(_approve(100), sim=lambda tx: {"will_revert": True, "error": "execution reverted"})
    assert "will_revert" in _codes(r) and r["ok"] is False
    assert r["simulation"]["will_revert"] is True


def test_sim_success_no_revert_flag():
    r = preflight(_approve(100), sim=lambda tx: {"will_revert": False})
    assert "will_revert" not in _codes(r)


# --- unit 6: send-path guard + export ---
def test_assert_safe_raises_on_high_flag():
    import pytest
    from chain_signer.preflight import assert_safe
    with pytest.raises(ValueError) as e:
        assert_safe(_approve(MAXU))
    assert "unlimited_approval" in str(e.value)


def test_assert_safe_passes_clean_tx_and_returns_report():
    from chain_signer.preflight import assert_safe
    rep = assert_safe(_approve(100))
    assert rep["ok"] is True


def test_assert_safe_force_overrides():
    from chain_signer.preflight import assert_safe
    rep = assert_safe(_approve(MAXU), force=True)  # force = sign anyway
    assert rep["ok"] is False  # still reports the danger, but does not raise


def test_preflight_exported_from_package():
    import chain_signer
    assert hasattr(chain_signer, "preflight") and hasattr(chain_signer, "assert_safe")
