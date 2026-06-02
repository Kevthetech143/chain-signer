"""Transaction preflight — decode an unsigned EVM tx and flag danger BEFORE signing.

chain-signer's safety layer: a FIRST-LINE check that catches common drain patterns (unlimited
approvals, approve-all, transferFrom pulls, proxy upgrades, reverts) before an agent signs. It is
a guard, NOT a guarantee — static calldata can lie, and signed-message (permit/Permit2) phishing
flows through sign_typed_data, not here. Fail-SAFE: never crashes on bad input; when unsure it
flags rather than waving through. Non-custodial: we only inspect and warn; the caller decides.
"""

# selector -> (name, [arg types]). 4-byte function selectors.
_KNOWN = {
    "0x095ea7b3": ("approve", ["address", "uint256"]),
    "0x39509351": ("increaseAllowance", ["address", "uint256"]),
    "0xa22cb465": ("setApprovalForAll", ["address", "bool"]),
    "0xa9059cbb": ("transfer", ["address", "uint256"]),
    "0x23b872dd": ("transferFrom", ["address", "address", "uint256"]),
    "0x3659cfe6": ("upgradeTo", ["address"]),
    "0x4f1ef286": ("upgradeToAndCall", ["address"]),
    # ERC-2612 permit submitted on-chain — grants an allowance to `spender` like approve does.
    "0xd505accf": ("permit", ["address", "address", "uint256", "uint256", "uint8", "bytes32", "bytes32"]),
}

_UNLIMITED_THRESHOLD = 1 << 255       # effectively-infinite approval (catches uint-max + half-max)
_LARGE_APPROVAL = 10 ** 24            # large-but-finite: warn, don't claim infinite
_MULTICALL = "0xac9650d8"             # multicall(bytes[]) — batches inner calls; drains hide here


def _norm_hex(data):
    if isinstance(data, (bytes, bytearray)):
        return data.hex()
    if not isinstance(data, str):
        return None
    return data[2:] if data[:2].lower() == "0x" else data


def _to_int(v):
    try:
        if v is None:
            return 0
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            return int(v, 16) if v[:2].lower() == "0x" else int(v)
        if isinstance(v, (bytes, bytearray)):
            return int.from_bytes(v, "big")
    except (ValueError, TypeError):
        return None
    return None


def _decode(data):
    """Decode calldata -> {function, selector, args, malformed}. Never raises."""
    s = _norm_hex(data)
    if not s:
        return None
    selector = "0x" + s[:8].lower()
    spec = _KNOWN.get(selector)
    if not spec:
        return {"function": None, "selector": selector, "args": [], "malformed": False}
    name, types = spec
    body = s[8:]
    args, malformed = [], False
    for i, t in enumerate(types):
        word = body[i * 64:(i + 1) * 64]
        if len(word) < 64:           # missing / truncated argument
            malformed = True
            break
        try:
            raw = int(word, 16)
        except ValueError:           # non-hex garbage in an arg word
            malformed = True
            break
        if t == "address":
            args.append("0x" + word[-40:])
        elif t == "bool":
            args.append(raw != 0)
        else:
            args.append(raw)
    return {"function": name, "selector": selector, "args": args, "malformed": malformed}


def _call_flags(decoded, prefix=""):
    """Risk flags for ONE decoded call. prefix tags calls found nested (e.g. inside multicall)."""
    flags = []
    if not decoded:
        return flags
    if decoded.get("malformed"):
        return [{"code": "malformed_call", "severity": "MED",
                 "detail": f"{prefix}calldata for {decoded.get('function') or 'a known function'} is truncated or "
                           "non-hex — its real effect can't be trusted; review before signing."}]
    fn, args = decoded.get("function"), decoded.get("args", [])
    if fn in ("approve", "increaseAllowance") and len(args) >= 2:
        amt, spender = args[1], args[0]
        if amt >= _UNLIMITED_THRESHOLD:
            flags.append({"code": "unlimited_approval", "severity": "HIGH",
                          "detail": f"{prefix}{fn}() grants an effectively-unlimited allowance to {spender} — "
                                    "a spender that turns malicious can drain that token."})
        elif amt >= _LARGE_APPROVAL:
            flags.append({"code": "large_approval", "severity": "MED",
                          "detail": f"{prefix}{fn}() grants a very large allowance to {spender}; confirm it's intended."})
    elif fn == "permit" and len(args) >= 3:
        spender, value = args[1], args[2]
        if value >= _UNLIMITED_THRESHOLD:
            flags.append({"code": "unlimited_approval", "severity": "HIGH",
                          "detail": f"{prefix}permit() grants an effectively-unlimited allowance to {spender} via a "
                                    "signed permit — a spender that turns malicious can drain that token."})
        elif value >= _LARGE_APPROVAL:
            flags.append({"code": "large_approval", "severity": "MED",
                          "detail": f"{prefix}permit() grants a very large allowance to {spender}; confirm it's intended."})
    elif fn == "setApprovalForAll" and len(args) >= 2 and args[1] is True:
        flags.append({"code": "approval_for_all", "severity": "HIGH",
                      "detail": f"{prefix}setApprovalForAll grants {args[0]} control of EVERY token in this "
                                "collection — a common NFT-drain approval."})
    elif fn == "transferFrom" and len(args) >= 3:
        flags.append({"code": "token_transfer_from", "severity": "HIGH",
                      "detail": f"{prefix}transferFrom moves tokens OUT of {args[0]} to {args[1]} — this is the call a "
                                "malicious spender uses to drain an approved wallet. Confirm you intend it."})
    elif fn == "transfer" and len(args) >= 2 and args[1] >= _LARGE_APPROVAL:
        flags.append({"code": "large_transfer", "severity": "MED",
                      "detail": f"{prefix}transfer of a very large amount to {args[0]}; confirm the amount/recipient."})
    elif fn in ("upgradeTo", "upgradeToAndCall"):
        flags.append({"code": "proxy_upgrade", "severity": "HIGH",
                      "detail": f"{prefix}{fn}() repoints a proxy's logic to {args[0] if args else '?'} — this can "
                                "replace the contract's entire behavior. Only sign if you control that address."})
    return flags


def _multicall_inner(data):
    """Return the inner calldata strings of a multicall(bytes[]), or None if not decodable."""
    try:
        from eth_abi import decode as _abidecode
        body = bytes.fromhex(_norm_hex(data)[8:])
        (calls,) = _abidecode(["bytes[]"], body)
        return ["0x" + c.hex() for c in calls]
    except Exception:
        return None


def preflight(tx, *, fetch=None, sim=None, max_value=None):
    """Inspect an unsigned EVM tx and return a risk report. Never signs/sends; never crashes."""
    if not isinstance(tx, dict):
        return {"decoded": None, "simulation": None, "ok": False,
                "risk_flags": [{"code": "unparseable", "severity": "HIGH",
                                "detail": "transaction is not a readable object — refusing to vouch for it."}]}

    data = tx.get("data") or "0x"
    s = _norm_hex(data) or ""
    selector = "0x" + s[:8].lower()
    decoded = _decode(data)
    flags = []

    if selector == _MULTICALL:
        inner = _multicall_inner(data)
        if inner is None:
            flags.append({"code": "malformed_call", "severity": "MED",
                          "detail": "multicall calldata couldn't be decoded — its inner calls can't be checked; review."})
        else:
            for c in inner:
                flags.extend(_call_flags(_decode(c), prefix="(inside multicall) "))
        decoded = {"function": "multicall", "selector": selector, "args": [], "malformed": False}
    else:
        flags.extend(_call_flags(decoded))
        if decoded is not None and decoded.get("function") is None and data not in ("0x", ""):
            flags.append({"code": "opaque_calldata", "severity": "LOW",
                          "detail": f"calldata calls an unknown function ({decoded.get('selector')}); "
                                    "can't tell what it does — review before signing."})

    value = _to_int(tx.get("value"))
    if value is None:
        flags.append({"code": "unreadable_value", "severity": "MED",
                      "detail": "transaction value couldn't be read — review before signing."})
    elif max_value is not None and value > max_value:
        flags.append({"code": "large_native_value", "severity": "MED",
                      "detail": f"about to send {value} wei to {tx.get('to')} — above your set limit; confirm."})

    simulation = None
    if sim is not None:
        try:
            simulation = sim(tx)
        except Exception as e:  # a broken simulator must not break the safety check
            simulation = {"will_revert": None, "error": f"simulation failed: {e}"}
        if simulation and simulation.get("will_revert"):
            flags.append({"code": "will_revert", "severity": "HIGH",
                          "detail": "simulation says this transaction will revert (fail) — signing wastes gas "
                                    f"and may not do what you expect. {simulation.get('error', '')}".strip()})

    ok = not any(f["severity"] == "HIGH" for f in flags)
    return {"decoded": decoded, "risk_flags": flags, "simulation": simulation, "ok": ok}


def assert_safe(tx, *, force=False, **kw):
    """Run preflight(tx); raise ValueError on a HIGH flag unless force=True. Returns the report."""
    report = preflight(tx, **kw)
    if not force:
        highs = [f for f in report["risk_flags"] if f["severity"] == "HIGH"]
        if highs:
            codes = ", ".join(f["code"] for f in highs)
            raise ValueError(f"preflight blocked this transaction (HIGH risk: {codes}). "
                             "Review the flags; pass force=True to sign anyway. "
                             + " | ".join(f["detail"] for f in highs))
    return report
