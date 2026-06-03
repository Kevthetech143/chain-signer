"""Signed-message / permit-phishing inspector — the off-chain sibling of preflight.

A drain doesn't need a malicious transaction. A dApp can ask the agent to SIGN an EIP-712 typed-data
message — most dangerously an ERC-2612 `permit` granting an unlimited token allowance to an attacker.
The agent signs it as if it were a harmless login; the attacker submits the signature on-chain and
drains. preflight() inspects transactions; this inspects what the agent is about to SIGN.

`inspect_typed_data(td)` decodes EIP-712 typed data and returns {decoded, risk_flags, ok}. Fail-safe:
never raises; flags rather than waving through what it can't read. A guard, not a guarantee.
"""
from .preflight import _to_int, _UNLIMITED_THRESHOLD, _LARGE_APPROVAL

# Permit2 amounts are uint160; its "unlimited" sentinel is type(uint160).max. A uint256-scale
# threshold would miss it, so Permit2 gets its own (catches the max + anything near it).
_PERMIT2_UNLIMITED = 1 << 159


def _permit2_flags(message):
    """Flags for a Permit2 PermitSingle/PermitBatch signature. details is a dict or a list of dicts."""
    flags = []
    spender = message.get("spender")
    details = message.get("details")
    items = details if isinstance(details, list) else [details]
    for d in items:
        if not isinstance(d, dict):
            continue
        amt = _to_int(d.get("amount"))
        if amt is None:
            continue
        if amt >= _PERMIT2_UNLIMITED:
            flags.append({"code": "unlimited_permit_signature", "severity": "HIGH",
                          "detail": f"signing this Permit2 grants an effectively-unlimited allowance for token "
                                    f"{d.get('token')} to {spender} — the Permit2 signature-phishing drain. "
                                    "Do not sign unless you trust the spender."})
        elif amt >= _LARGE_APPROVAL:
            flags.append({"code": "large_permit_signature", "severity": "MED",
                          "detail": f"signing this Permit2 grants a very large allowance for token {d.get('token')} "
                                    f"to {spender}; confirm it's intended."})
    return flags


def inspect_typed_data(td, *, max_value=None):
    """Inspect an EIP-712 typed-data object the agent is about to sign. Never raises."""
    if not isinstance(td, dict):
        return {"decoded": None, "risk_flags": [{"code": "unparseable", "severity": "HIGH",
                "detail": "typed data is not a readable object — refusing to vouch for this signature."}],
                "ok": False}

    primary = td.get("primaryType")
    message = td.get("message") if isinstance(td.get("message"), dict) else {}
    flags = []

    # ERC-2612 permit: signing this grants an allowance off-chain, just like approve() on-chain.
    if primary == "Permit":
        spender = message.get("spender")
        # DAI-style permit(holder, spender, nonce, expiry, allowed): no `value`; allowed=true == unlimited.
        if "allowed" in message and "value" not in message:
            if message.get("allowed") is True:
                flags.append({"code": "unlimited_permit_signature", "severity": "HIGH",
                              "detail": f"signing this DAI-style permit (allowed=true) grants an UNLIMITED token "
                                        f"allowance to {spender} — the classic signature-phishing drain. Do not "
                                        "sign unless you trust the spender."})
            decoded = {"primaryType": primary, "verifyingContract": (td.get("domain") or {}).get("verifyingContract")}
            return {"decoded": decoded, "risk_flags": flags,
                    "ok": not any(f["severity"] == "HIGH" for f in flags)}
        value = _to_int(message.get("value"))
        if value is None:
            flags.append({"code": "unreadable_permit_value", "severity": "MED",
                          "detail": "permit signature whose allowance amount can't be read — review before signing."})
        elif value >= _UNLIMITED_THRESHOLD:
            flags.append({"code": "unlimited_permit_signature", "severity": "HIGH",
                          "detail": f"signing this permit grants an effectively-unlimited token allowance to "
                                    f"{spender} — a spender that turns malicious can then drain that token. This is "
                                    "the classic signature-phishing drain. Do not sign unless you trust the spender."})
        elif value >= _LARGE_APPROVAL:
            flags.append({"code": "large_permit_signature", "severity": "MED",
                          "detail": f"signing this permit grants a very large token allowance to {spender}; "
                                    "confirm it's intended."})

    # Permit2 (Uniswap): PermitSingle / PermitBatch — same drain, uint160 amounts.
    elif primary in ("PermitSingle", "PermitBatch"):
        flags.extend(_permit2_flags(message))

    decoded = {"primaryType": primary, "verifyingContract": (td.get("domain") or {}).get("verifyingContract")}
    ok = not any(f["severity"] == "HIGH" for f in flags)
    return {"decoded": decoded, "risk_flags": flags, "ok": ok}
