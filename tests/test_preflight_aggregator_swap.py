"""Adversarial angle (2026-06-09): preflight decodes Uniswap Universal Router Permit2 commands
and every wrapper entrypoint (multicall, execute, execTransaction, DSProxy) — but NOT the
1inch / 0x DEX aggregator swap entrypoints that AI-agent frameworks sign directly.

The attack shape is a NEW type (the swap's OWN parameters, not a wrapper hiding an inner drain):
  • 1inch AggregationRouter v5 swap(executor, SwapDescription, permit, data)
      SwapDescription = (srcToken, dstToken, srcReceiver, dstReceiver, amount, minReturnAmount, flags)
      dstReceiver != tx.from  -> output redirected to a third party    (HIGH, swap_output_redirected)
      minReturnAmount == 0    -> slippage rail removed / zero minimum  (HIGH, swap_zero_slippage)
  • 0x ExchangeProxy transformERC20(inputToken, outputToken, inputAmount, minOutputAmount, transformations)
      minOutputAmount == 0    -> zero slippage protection              (HIGH, swap_zero_slippage)
      output always goes to msg.sender (no recipient param) -> no redirect check

EVIDENCE that this is REAL: SwapNet/Aperture ~$17M drained via attacker-controlled dstReceiver;
1inch Fusion v1 ~$5M calldata corruption forcing minReturnAmount=0; keyless agent frameworks fetch
ready-to-exec aggregator calldata and sign it blind. Named defenses = decode + assert dstReceiver and
minReturnAmount — EXACTLY what preflight is for.

Selectors verified against 4byte.directory:
  0x12aa3caf = swap(address,(address,address,address,address,uint256,uint256,uint256),bytes,bytes)
  0x415565b0 = transformERC20(address,address,uint256,uint256,(uint32,bytes)[])
"""
from eth_abi import encode
from chain_signer.preflight import preflight, assert_safe
import pytest

# --- address constants ---
CALLER = "0x" + "aa" * 20        # tx.from — the agent's address
ATTACKER = "0x" + "ee" * 20      # third-party output recipient (drain target)
TOKEN_IN = "0x" + "11" * 20      # input token (e.g. USDC)
TOKEN_OUT = "0x" + "22" * 20     # output token (e.g. ETH)
ROUTER = "0x" + "55" * 20        # aggregator router address
EXECUTOR = "0x" + "66" * 20      # 1inch executor address

ONE_INCH_SWAP_SEL = "0x12aa3caf"
ZERO_X_TRANSFORM_SEL = "0x415565b0"


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _tx(data, to=ROUTER, frm=CALLER):
    return {"to": to, "data": data, "value": 0, "from": frm}


# --- 1inch calldata builders ---
def _1inch_swap(
    src_token=TOKEN_IN,
    dst_token=TOKEN_OUT,
    src_receiver=EXECUTOR,
    dst_receiver=CALLER,     # safe default: output goes to caller
    amount=10 ** 18,
    min_return=10 ** 17,     # 10% slippage tolerance (non-zero)
    flags=0,
    permit=b"",
    data=b"",
):
    """Build 1inch AggregationRouter v5 swap() calldata."""
    desc = (src_token, dst_token, src_receiver, dst_receiver, amount, min_return, flags)
    body = encode(
        ["address", "(address,address,address,address,uint256,uint256,uint256)", "bytes", "bytes"],
        [EXECUTOR, desc, permit, data],
    )
    return ONE_INCH_SWAP_SEL + body.hex()


# --- 0x calldata builders ---
def _0x_transform(
    input_token=TOKEN_IN,
    output_token=TOKEN_OUT,
    input_amount=10 ** 18,
    min_output=10 ** 17,     # non-zero by default
    transformations=None,
):
    """Build 0x ExchangeProxy transformERC20() calldata."""
    if transformations is None:
        transformations = []   # empty list — ABI shape still valid
    body = encode(
        ["address", "address", "uint256", "uint256", "(uint32,bytes)[]"],
        [input_token, output_token, input_amount, min_output, transformations],
    )
    return ZERO_X_TRANSFORM_SEL + body.hex()


# ============================================================
# 1inch: dstReceiver redirect (HIGH — swap_output_redirected)
# ============================================================

def test_1inch_swap_dst_receiver_redirected_to_attacker_is_high():
    """dstReceiver != tx.from — output stolen by third party — must flag HIGH."""
    data = _1inch_swap(dst_receiver=ATTACKER)
    r = preflight(_tx(data))
    assert "swap_output_redirected" in _codes(r)
    assert r["ok"] is False


def test_1inch_swap_dst_receiver_redirected_hard_stops():
    """assert_safe must raise on a redirected swap."""
    data = _1inch_swap(dst_receiver=ATTACKER)
    with pytest.raises(ValueError):
        assert_safe(_tx(data))


# ============================================================
# 1inch: minReturnAmount == 0 (HIGH — swap_zero_slippage)
# ============================================================

def test_1inch_swap_min_return_zero_is_high():
    """minReturnAmount = 0 removes slippage rail — flag HIGH."""
    data = _1inch_swap(min_return=0)
    r = preflight(_tx(data))
    assert "swap_zero_slippage" in _codes(r)
    assert r["ok"] is False


def test_1inch_swap_min_return_zero_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_1inch_swap(min_return=0)))


def test_1inch_swap_redirect_and_zero_slippage_both_flagged():
    """Both failure modes in one call — both flags must appear."""
    data = _1inch_swap(dst_receiver=ATTACKER, min_return=0)
    r = preflight(_tx(data))
    codes = _codes(r)
    assert "swap_output_redirected" in codes
    assert "swap_zero_slippage" in codes
    assert r["ok"] is False


# ============================================================
# 1inch: benign / clean swap (no flags)
# ============================================================

def test_1inch_swap_benign_output_to_caller_is_clean():
    """dst_receiver == tx.from, non-zero min_return — must NOT flag."""
    data = _1inch_swap(dst_receiver=CALLER, min_return=10 ** 17)
    r = preflight(_tx(data))
    assert "swap_output_redirected" not in _codes(r)
    assert "swap_zero_slippage" not in _codes(r)
    assert r["ok"] is True


def test_1inch_swap_malformed_calldata_does_not_crash():
    """Truncated / garbage calldata must not raise — surface gracefully."""
    bad = ONE_INCH_SWAP_SEL + "dead" * 4
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r


# ============================================================
# 0x: minOutputTokenAmount == 0 (HIGH — swap_zero_slippage)
# ============================================================

def test_0x_transform_min_output_zero_is_high():
    """minOutputTokenAmount = 0 removes slippage rail — flag HIGH."""
    data = _0x_transform(min_output=0)
    r = preflight(_tx(data))
    assert "swap_zero_slippage" in _codes(r)
    assert r["ok"] is False


def test_0x_transform_min_output_zero_hard_stops():
    with pytest.raises(ValueError):
        assert_safe(_tx(_0x_transform(min_output=0)))


# ============================================================
# 0x: benign swap (no flags)
# ============================================================

def test_0x_transform_benign_non_zero_min_is_clean():
    """Non-zero minOutputTokenAmount — must NOT flag."""
    data = _0x_transform(min_output=10 ** 17)
    r = preflight(_tx(data))
    assert "swap_zero_slippage" not in _codes(r)
    assert r["ok"] is True


def test_0x_transform_malformed_does_not_crash():
    """Truncated calldata must not raise."""
    bad = ZERO_X_TRANSFORM_SEL + "be" * 8
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r
