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


def _allowed_is_true(v):
    """DAI permit `allowed` is a bool on-chain, but a hostile dApp controls the JSON it asks us to
    sign and can encode "true" as 1 / "1" / "0x1" / "true" — all of which the on-chain verifier reads
    as true and grant an UNLIMITED allowance. Treat every such encoding as true; only false/0/"" is safe."""
    if v is True:
        return True
    if v is False or v is None:
        return False
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes"):
            return True
        if s in ("false", "no", ""):
            return False
    i = _to_int(v)
    return i is not None and i != 0


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


def _permit2_transfer_flags(message):
    """Permit2 SignatureTransfer (PermitTransferFrom/Batch): flag ONLY an unlimited permitted amount
    — legit apps authorize an exact amount, so we don't cry wolf on large-but-specific transfers."""
    flags = []
    spender = message.get("spender")
    permitted = message.get("permitted")
    items = permitted if isinstance(permitted, list) else [permitted]
    for d in items:
        if not isinstance(d, dict):
            continue
        amt = _to_int(d.get("amount"))
        if amt is not None and amt >= _PERMIT2_UNLIMITED:
            flags.append({"code": "unlimited_permit_signature", "severity": "HIGH",
                          "detail": f"signing this Permit2 transfer authorizes {spender} to pull an effectively-"
                                    f"unlimited amount of token {d.get('token')} — a signature-transfer drain. "
                                    "Legit transfers use an exact amount; do not sign this."})
    return flags


def _seaport_flags(message):
    """Flag a Seaport order that GIVES ASSETS AWAY for nothing: the `offer` is non-empty but the
    `consideration` is empty or all-zero. A legitimate listing always pays the seller, so this stays
    non-noisy — we do NOT flag normal-priced listings. This is the off-chain NFT-drain sibling of
    setApprovalForAll (a signed marketplace order, not a transaction)."""
    flags = []
    offer = message.get("offer")
    if not isinstance(offer, list) or not offer:
        return flags                       # nothing offered -> nothing to give away
    consideration = message.get("consideration")
    items = consideration if isinstance(consideration, list) else []
    total = 0
    for c in items:
        if isinstance(c, dict):
            amt = _to_int(c.get("startAmount"))
            if amt:
                total += amt
    if total == 0:                         # consideration empty OR every amount zero/unreadable
        flags.append({"code": "seaport_zero_consideration", "severity": "HIGH",
                      "detail": "signing this Seaport order gives away the offered asset(s) for ZERO "
                                "consideration — the NFT/marketplace signature-phishing drain. A real "
                                "listing always pays the seller; do not sign unless you intend a gift."})
    return flags


def inspect_typed_data(td, *, max_value=None):
    """Inspect an EIP-712 typed-data object the agent is about to sign. Never raises."""
    if not isinstance(td, dict):
        return {"decoded": None, "risk_flags": [{"code": "unparseable", "severity": "HIGH",
                "detail": "typed data is not a readable object — refusing to vouch for this signature."}],
                "ok": False}

    primary = td.get("primaryType")
    # Normalize for matching — a security tool must not be defeated by casing/whitespace.
    pnorm = primary.strip().lower() if isinstance(primary, str) else ""
    message = td.get("message") if isinstance(td.get("message"), dict) else {}
    flags = []

    # ERC-2612 permit: signing this grants an allowance off-chain, just like approve() on-chain.
    if pnorm == "permit":
        spender = message.get("spender")
        # DAI-style permit(holder, spender, nonce, expiry, allowed): allowed=true == unlimited.
        # Detect off the PRESENCE of `allowed`, never off the ABSENCE of `value` — EIP-712 hashes only
        # the fields declared in `types`, so a hostile dApp can add a decoy `value` key the on-chain
        # verifier ignores while still signing allowed=true. allowed:true is unlimited regardless.
        dai_allowed = "allowed" in message
        if dai_allowed and _allowed_is_true(message.get("allowed")):
            flags.append({"code": "unlimited_permit_signature", "severity": "HIGH",
                          "detail": f"signing this DAI-style permit (allowed=true) grants an UNLIMITED token "
                                    f"allowance to {spender} — the classic signature-phishing drain. Do not "
                                    "sign unless you trust the spender."})
        # ERC-2612 value path — runs when a `value` is present (a real ERC-2612 permit, or a decoy
        # alongside a DAI permit). A bare DAI permit (allowed only, no value) skips this; missing
        # value would read as 0 and is not a drain.
        if "value" in message:
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

    # Permit2 (Uniswap): PermitSingle / PermitBatch — allowance permits, uint160 amounts.
    elif pnorm in ("permitsingle", "permitbatch"):
        flags.extend(_permit2_flags(message))

    # Permit2 SignatureTransfer — authorizes a pull; flag only unlimited (legit uses exact amounts).
    elif pnorm in ("permittransferfrom", "permitbatchtransferfrom"):
        flags.extend(_permit2_transfer_flags(message))

    # Seaport order — a signed marketplace order that gives assets away for zero consideration.
    elif pnorm == "ordercomponents":
        flags.extend(_seaport_flags(message))

    decoded = {"primaryType": primary, "verifyingContract": (td.get("domain") or {}).get("verifyingContract")}
    ok = not any(f["severity"] == "HIGH" for f in flags)
    return {"decoded": decoded, "risk_flags": flags, "ok": ok}
