"""Transaction preflight — decode an unsigned EVM tx and flag danger BEFORE signing.

chain-signer's safety wedge: "the agent signer that won't sign a dangerous transaction."
Given an unsigned tx ({to, data, value, ...}), preflight() decodes the calldata and returns
risk flags so an agent (or our send path) can refuse a drain/unlimited-approval/etc. before it
signs. Pure, offline, deterministic — no network needed for the static checks (richer simulation
is injectable). Non-custodial: we only inspect and warn; the caller stays in control.
"""

# selector -> (name, [arg types]). 4-byte function selectors (keccak of the signature, first 4 bytes).
_KNOWN = {
    "0x095ea7b3": ("approve", ["address", "uint256"]),          # ERC-20 approve(spender, amount)
    "0xa22cb465": ("setApprovalForAll", ["address", "bool"]),   # ERC-721/1155 setApprovalForAll(op, approved)
}

# An approval at/near uint256-max is the classic "infinite approval" drain vector.
_UNLIMITED_THRESHOLD = (1 << 256) - (1 << 240)  # ~uint256 max; tolerant of common max-ish values


def _decode(data):
    """Decode calldata into {function, selector, args} for known functions, else None."""
    if not data or data == "0x":
        return None
    hexstr = data[2:] if data.startswith("0x") else data
    selector = "0x" + hexstr[:8].lower()
    spec = _KNOWN.get(selector)
    if not spec:
        return {"function": None, "selector": selector, "args": []}
    name, types = spec
    body = hexstr[8:]
    args = []
    for i, t in enumerate(types):
        word = body[i * 64:(i + 1) * 64]
        if not word:
            break
        if t == "address":
            args.append("0x" + word[-40:])
        elif t == "bool":
            args.append(int(word, 16) != 0)
        else:  # uint256 and friends
            args.append(int(word, 16))
    return {"function": name, "selector": selector, "args": args}


def preflight(tx, *, fetch=None, sim=None, max_value=None):
    """Inspect an unsigned EVM tx and return a risk report. Does NOT sign or send.

    sim: optional callable(tx)->{"will_revert": bool, ...} for richer simulation (injectable, so
    tests/offline use need no chain). max_value: flag native sends above this (wei).
    """
    decoded = _decode(tx.get("data"))
    data = tx.get("data") or "0x"
    flags = []

    if decoded and decoded["function"] == "approve" and len(decoded["args"]) >= 2:
        amount = decoded["args"][1]
        if isinstance(amount, int) and amount >= _UNLIMITED_THRESHOLD:
            flags.append({"code": "unlimited_approval", "severity": "HIGH",
                          "detail": f"approve() grants a near-unlimited allowance to {decoded['args'][0]} "
                                    "— a spender that turns malicious can drain that token."})

    if decoded and decoded["function"] == "setApprovalForAll" and len(decoded["args"]) >= 2:
        if decoded["args"][1] is True:
            flags.append({"code": "approval_for_all", "severity": "HIGH",
                          "detail": f"setApprovalForAll grants {decoded['args'][0]} control of EVERY token "
                                    "in this collection — a common NFT-drain approval."})

    # native value over the caller's comfort threshold
    value = int(tx.get("value") or 0)
    if max_value is not None and value > max_value:
        flags.append({"code": "large_native_value", "severity": "MED",
                      "detail": f"about to send {value} wei to {tx.get('to')} — above your set limit; confirm."})

    # non-empty calldata to a function we can't decode = we can't tell what it does
    if decoded is not None and decoded.get("function") is None and data not in ("0x", ""):
        flags.append({"code": "opaque_calldata", "severity": "LOW",
                      "detail": f"calldata calls an unknown function ({decoded.get('selector')}); "
                                "can't tell what it does — review before signing."})

    simulation = None
    if sim is not None:
        simulation = sim(tx)
        if simulation and simulation.get("will_revert"):
            flags.append({"code": "will_revert", "severity": "HIGH",
                          "detail": "simulation says this transaction will revert (fail) — signing wastes gas "
                                    f"and may not do what you expect. {simulation.get('error', '')}".strip()})

    ok = not any(f["severity"] == "HIGH" for f in flags)
    return {"decoded": decoded, "risk_flags": flags, "simulation": simulation, "ok": ok}


def assert_safe(tx, *, force=False, **kw):
    """Run preflight(tx); raise ValueError if a HIGH flag is present (unless force=True).

    The send-path guard: build a tx, assert_safe() it, then sign. Returns the report either way.
    force=True signs anyway but still returns the (not-ok) report so the caller has the warnings.
    """
    report = preflight(tx, **kw)
    if not force:
        highs = [f for f in report["risk_flags"] if f["severity"] == "HIGH"]
        if highs:
            codes = ", ".join(f["code"] for f in highs)
            raise ValueError(f"preflight blocked this transaction (HIGH risk: {codes}). "
                             "Review the flags; pass force=True to sign anyway. "
                             + " | ".join(f["detail"] for f in highs))
    return report
