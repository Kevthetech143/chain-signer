"""Adversarial angle (2026-06-08): preflight recursed into multicall, ERC-4337 execute/executeBatch
and Safe multiSend, but NOT into the Uniswap UNIVERSAL ROUTER. The Universal Router is the dominant
swap/approval entrypoint in the EVM agent niche — and its calldata is shaped UNLIKE every wrapper we
already cover: `execute(bytes commands, bytes[] inputs[, uint256 deadline])` where each command is a
single byte (low 7 bits = command type, high bit 0x80 = allow-revert) and inputs[i] is a RAW ABI tuple
with NO inner 4-byte selector. So a drain routed through it — a PERMIT2_PERMIT granting an unlimited
uint160 allowance, or a PERMIT2_TRANSFER_FROM pulling tokens straight to the attacker — flowed through
preflight as a single opaque LOW call: ok=True, assert_safe PASSED (empirically confirmed fail-OPEN).
Same evasion CLASS as the v0.5.19 ERC-4337 execute gap and the v0.5.20 Seaport BulkOrder gap: a covered
drain hidden behind an uncovered wrapper/encoding.

Fix: decode the command bytes + ABI-tuple inputs and emit flags directly for the dangerous Permit2
commands (the existing selector-based recursion can't help — there is no inner selector). Non-noisy by
construction: a plain swap (V3/V2_SWAP, WRAP/UNWRAP) carries no Permit2-approval/transfer command, so it
stays clean exactly as today. Command bytes verified against Uniswap's live Commands.sol:
PERMIT2_TRANSFER_FROM=0x02, PERMIT2_PERMIT_BATCH=0x03, PERMIT2_PERMIT=0x0a,
PERMIT2_TRANSFER_FROM_BATCH=0x0d, EXECUTE_SUB_PLAN=0x21, COMMAND_TYPE_MASK=0x7f, FLAG_ALLOW_REVERT=0x80.
"""
from eth_abi import encode
from chain_signer.preflight import preflight, assert_safe
import pytest

ATTACKER = "0x" + "ee" * 20
TOKEN = "0x" + "33" * 20
VICTIM = "0x" + "11" * 20
MAX_U160 = (1 << 160) - 1

# Universal Router selectors
EXEC3 = "0x3593564c"   # execute(bytes,bytes[],uint256)
EXEC2 = "0x24856bc3"   # execute(bytes,bytes[])

# command type bytes
C_V3_SWAP = 0x00
C_PERMIT2_TRANSFER_FROM = 0x02
C_PERMIT2_PERMIT_BATCH = 0x03
C_PERMIT2_PERMIT = 0x0a
C_WRAP_ETH = 0x0b
C_PERMIT2_TRANSFER_FROM_BATCH = 0x0d
C_EXECUTE_SUB_PLAN = 0x21
FLAG_ALLOW_REVERT = 0x80


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


# --- input builders (raw ABI tuples, NO selector) ---

def _in_transfer_from(token=TOKEN, recipient=ATTACKER, amount=10 ** 18):
    return encode(["address", "address", "uint160"], [token, recipient, amount])


def _in_permit(amount=MAX_U160, spender=ATTACKER, token=TOKEN):
    permit_single = ((token, amount, 0, 0), spender, 2 ** 32)
    return encode(["((address,uint160,uint48,uint48),address,uint256)", "bytes"], [permit_single, b""])


def _in_permit_batch(amount=MAX_U160, spender=ATTACKER, token=TOKEN):
    permit_batch = ([(token, amount, 0, 0)], spender, 2 ** 32)
    return encode(["((address,uint160,uint48,uint48)[],address,uint256)", "bytes"], [permit_batch, b""])


def _in_transfer_from_batch(token=TOKEN, to=ATTACKER, amount=10 ** 18):
    # AllowanceTransferDetails[] = (from, to, amount, token)[]
    return encode(["(address,address,uint160,address)[]"], [[(VICTIM, to, amount, token)]])


def _in_sub_plan(commands, inputs):
    return encode(["bytes", "bytes[]"], [commands, inputs])


def _ur3(commands, inputs, deadline=2 ** 32):
    return EXEC3 + encode(["bytes", "bytes[]", "uint256"], [commands, inputs, deadline]).hex()


def _ur2(commands, inputs):
    return EXEC2 + encode(["bytes", "bytes[]"], [commands, inputs]).hex()


def _tx(data):
    return {"to": "0x" + "44" * 20, "data": data, "value": 0}


# --- the drain must be caught ---

def test_ur_permit2_transfer_from_to_attacker_is_high():
    data = _ur3(bytes([C_PERMIT2_TRANSFER_FROM]), [_in_transfer_from()])
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r)
    assert r["ok"] is False


def test_ur_permit2_transfer_from_hard_stops():
    data = _ur3(bytes([C_PERMIT2_TRANSFER_FROM]), [_in_transfer_from()])
    with pytest.raises(ValueError):
        assert_safe(_tx(data))


def test_ur_permit2_permit_unlimited_is_high():
    data = _ur3(bytes([C_PERMIT2_PERMIT]), [_in_permit(MAX_U160)])
    r = preflight(_tx(data))
    assert "unlimited_approval" in _codes(r)
    assert r["ok"] is False


def test_ur_two_arg_variant_transfer_from_is_high():
    data = _ur2(bytes([C_PERMIT2_TRANSFER_FROM]), [_in_transfer_from()])
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_ur_permit2_permit_batch_unlimited_is_high():
    data = _ur3(bytes([C_PERMIT2_PERMIT_BATCH]), [_in_permit_batch(MAX_U160)])
    r = preflight(_tx(data))
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


def test_ur_permit2_transfer_from_batch_is_high():
    data = _ur3(bytes([C_PERMIT2_TRANSFER_FROM_BATCH]), [_in_transfer_from_batch()])
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_ur_allow_revert_flag_does_not_mask_command():
    # high bit 0x80 = allow-revert; the command type is the low 7 bits. A drainer can set it.
    data = _ur3(bytes([FLAG_ALLOW_REVERT | C_PERMIT2_TRANSFER_FROM]), [_in_transfer_from()])
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_ur_drain_among_clean_commands_is_high():
    # a real bundle: swap then a hidden permit-unlimited. The clean swap input is opaque to us; the
    # drain still surfaces.
    commands = bytes([C_V3_SWAP, C_PERMIT2_PERMIT])
    inputs = [b"\x00" * 32, _in_permit(MAX_U160)]
    r = preflight(_tx(_ur3(commands, inputs)))
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


# --- nesting: same evasion class one layer down ---

def test_erc4337_execute_wrapping_ur_drain_is_high():
    ur = bytes.fromhex(_ur3(bytes([C_PERMIT2_TRANSFER_FROM]), [_in_transfer_from()])[2:])
    data = "0xb61d27f6" + encode(["address", "uint256", "bytes"],
                                  ["0x" + "44" * 20, 0, ur]).hex()
    r = preflight(_tx(data))
    assert "token_transfer_from" in _codes(r) and r["ok"] is False


def test_ur_execute_sub_plan_hiding_drain_is_high():
    # EXECUTE_SUB_PLAN (0x21) carries a nested (commands, inputs) — a drain can sit inside it.
    sub = _in_sub_plan(bytes([C_PERMIT2_PERMIT]), [_in_permit(MAX_U160)])
    data = _ur3(bytes([C_EXECUTE_SUB_PLAN]), [sub])
    r = preflight(_tx(data))
    assert "unlimited_approval" in _codes(r) and r["ok"] is False


# --- non-noisy: benign Universal Router calls must stay clean ---

def test_ur_plain_swap_not_flagged():
    # V3_SWAP_EXACT_IN + WRAP_ETH, no Permit2 approval/transfer command — a normal swap.
    commands = bytes([C_WRAP_ETH, C_V3_SWAP])
    inputs = [b"\x00" * 32, b"\x00" * 64]
    r = preflight(_tx(_ur3(commands, inputs)))
    assert "token_transfer_from" not in _codes(r)
    assert "unlimited_approval" not in _codes(r)
    assert r["ok"] is True


def test_ur_permit2_permit_exact_amount_not_unlimited():
    # an exact-amount permit (not type(uint160).max) must NOT raise the unlimited flag.
    data = _ur3(bytes([C_PERMIT2_PERMIT]), [_in_permit(1000)])
    r = preflight(_tx(data))
    assert "unlimited_approval" not in _codes(r)


def test_ur_malformed_does_not_crash():
    bad = EXEC3 + "00" * 4   # truncated args
    r = preflight(_tx(bad))
    assert isinstance(r, dict) and "risk_flags" in r
