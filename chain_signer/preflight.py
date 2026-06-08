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
    # ERC-721 / ERC-1155 safe transfers — same drain shape as transferFrom (from -> to). Only the
    # first two words (from, to) are needed; trailing dynamic args are ignored.
    "0x42842e0e": ("safeTransferFrom", ["address", "address"]),         # ERC-721
    "0xb88d4fde": ("safeTransferFrom", ["address", "address"]),         # ERC-721 with data
    "0xf242432a": ("safeTransferFrom", ["address", "address"]),         # ERC-1155
    "0x2eb2c2d6": ("safeBatchTransferFrom", ["address", "address"]),    # ERC-1155 batch
    "0x3659cfe6": ("upgradeTo", ["address"]),
    "0x4f1ef286": ("upgradeToAndCall", ["address"]),
    # ERC-2612 permit submitted on-chain — grants an allowance to `spender` like approve does.
    "0xd505accf": ("permit", ["address", "address", "uint256", "uint256", "uint8", "bytes32", "bytes32"]),
    # DAI-style permit submitted on-chain — different shape (no amount; a bool `allowed`). allowed=true
    # grants an effectively-unlimited allowance to `spender`; allowed=false REVOKES. Only first 5 args
    # are needed (trailing v,r,s ignored). permit(holder, spender, nonce, expiry, allowed, v, r, s).
    "0x8fcbaf0c": ("daiPermit", ["address", "address", "uint256", "uint256", "bool"]),
    # Permit2 (Uniswap's universal approval router, used by most aggregators) — its ON-CHAIN calls flow
    # through here as plain txs. approve grants an allowance; transferFrom is the drain-pull counterpart.
    # NOTE arg ORDER differs from ERC-20: spender is the 2nd arg, amount the 3rd; amount is uint160.
    "0x87517c45": ("permit2Approve", ["address", "address", "uint160", "uint48"]),
    "0x36c78516": ("permit2TransferFrom", ["address", "address", "uint160", "address"]),
}

# Permit2 permit() — submitting a signed permit ON-CHAIN writes the SAME (spender -> uint160 allowance)
# state that permit2Approve writes, so flagging approve but not permit leaves a trivial bypass. The
# amount lives inside a tuple (single) / tuple-array (batch), so these need real ABI decoding, not the
# flat fixed-offset path. permit(owner, PermitSingle/PermitBatch, signature).
_PERMIT2_PERMIT_SINGLE = "0x2b67b570"
_PERMIT2_PERMIT_BATCH = "0x2a2d80d1"
_PERMIT2_PERMIT_TYPES = {
    _PERMIT2_PERMIT_SINGLE: ["address", "((address,uint160,uint48,uint48),address,uint256)", "bytes"],
    _PERMIT2_PERMIT_BATCH: ["address", "((address,uint160,uint48,uint48)[],address,uint256)", "bytes"],
}

_UNLIMITED_THRESHOLD = 10 ** 40       # effectively-infinite approval. A drainer needn't use uint256-max:
                                      # any amount beyond every real ERC-20's total supply (largest are
                                      # ~1e33 base units) is a full drain. 1e40 sits ~7 orders above that
                                      # — no legit approval reaches it — yet well below sub-max evasions
                                      # (2**160/200/240) that previously slipped to MED and dodged the hard-stop.
_UNLIMITED_U160 = 1 << 159            # Permit2 amount is uint160 — its "infinite" is type(uint160).max,
                                      # far below the uint256 threshold; catch the top half of the range
_LARGE_APPROVAL = 10 ** 24            # large-but-finite: warn, don't claim infinite
_MULTICALL = "0xac9650d8"             # multicall(bytes[]) — batches inner calls; drains hide here
# Every multicall variant we know maps selector -> ABI arg types; the bytes[] arg holds inner calls.
# Routers in the wild use more than the bare form — Uniswap V3/V4 use the deadline/blockhash variants.
_MULTICALL_VARIANTS = {
    "0xac9650d8": ["bytes[]"],                       # multicall(bytes[])
    "0x5ae401dc": ["uint256", "bytes[]"],            # multicall(uint256 deadline, bytes[])  — Uniswap
    "0x1f0464d1": ["bytes32", "bytes[]"],            # multicall(bytes32 prevBlockhash, bytes[]) — Uniswap
    "0x525f7b5e": ["uint256", "bytes32", "bytes[]"], # multicall(uint256, bytes32, bytes[])
}
_MAX_MULTICALL_DEPTH = 5              # guard against a malicious deeply-nested multicall bomb

# ERC-4337 / smart-account execute wrappers. An agent's smart wallet (ERC-4337 account, Gnosis Safe)
# does NOT call approve()/transferFrom() directly — it routes every action through one of these. A
# drain wrapped one layer down (execute(token, 0, approve(attacker, MAX))) is invisible unless we
# unwrap it, exactly like a drain hidden in a multicall. execute() carries ONE inner call; the
# executeBatch / multiSend forms carry many. We recurse into the inner call(s) and flag only on what
# they are — a benign execute (clean swap, exact approval, bare ETH transfer) stays clean.
_EXEC_SINGLE = {
    "0xb61d27f6": ["address", "uint256", "bytes"],          # execute(address,uint256,bytes)
}
_EXEC_BATCH = {
    "0x47e1da2a": ["address[]", "uint256[]", "bytes[]"],    # executeBatch(address[],uint256[],bytes[])
    "0x18dfb3c7": ["address[]", "bytes[]"],                 # executeBatch(address[],bytes[])
}
_MULTISEND = "0x8d80ff0a"                                   # Gnosis Safe multiSend(bytes) — packed encoding
# Every selector that wraps inner calldata we must unwrap before judging.
_WRAPPER_SELECTORS = set(_MULTICALL_VARIANTS) | set(_EXEC_SINGLE) | set(_EXEC_BATCH) | {_MULTISEND}

# Uniswap UNIVERSAL ROUTER — the dominant swap/approval entrypoint in the EVM agent niche. Unlike every
# wrapper above, its inner calls are NOT selector-prefixed calldata: execute(bytes commands, bytes[]
# inputs[, uint256 deadline]) carries ONE byte per command (low 7 bits = command type, high bit 0x80 =
# allow-revert) and inputs[i] is a RAW ABI tuple. So the selector-based recursion can't reach a drain
# routed through it — we decode the command bytes and the dangerous Permit2 inputs directly.
_UR_EXEC = {
    "0x3593564c": ["bytes", "bytes[]", "uint256"],   # execute(commands, inputs, deadline)
    "0x24856bc3": ["bytes", "bytes[]"],              # execute(commands, inputs)
}
_UR_COMMAND_TYPE_MASK = 0x7f                          # low 7 bits = command type; 0x80 = allow-revert flag
# command type bytes (verified against Uniswap's live Commands.sol)
_UR_PERMIT2_TRANSFER_FROM = 0x02
_UR_PERMIT2_PERMIT_BATCH = 0x03
_UR_PERMIT2_PERMIT = 0x0a
_UR_PERMIT2_TRANSFER_FROM_BATCH = 0x0d
_UR_EXECUTE_SUB_PLAN = 0x21                           # carries a nested (commands, inputs) — recurse


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
    except (ValueError, TypeError, OverflowError):  # OverflowError: int(float('inf'))
        return None
    return None


def _decode_permit2_permit(selector, body_hex):
    """Decode Permit2 permit (single/batch) via real ABI decode -> (spender, worst_amount) or None."""
    try:
        raw = bytes.fromhex(body_hex)
        from eth_abi import decode as _abidecode
        owner, permit, sig = _abidecode(_PERMIT2_PERMIT_TYPES[selector], raw)
        if selector == _PERMIT2_PERMIT_SINGLE:
            details, spender, _deadline = permit          # details = (token, amount, exp, nonce)
            amount = details[1]
        else:
            details_arr, spender, _deadline = permit       # details_arr = [(token, amount, exp, nonce), ...]
            amount = max((d[1] for d in details_arr), default=0)
        return spender, amount
    except Exception:                                       # malformed / not real Permit2 calldata
        return None


def _decode(data):
    """Decode calldata -> {function, selector, args, malformed}. Never raises."""
    s = _norm_hex(data)
    if not s:
        return None
    selector = "0x" + s[:8].lower()
    if selector in _PERMIT2_PERMIT_TYPES:
        res = _decode_permit2_permit(selector, s[8:])
        if res is None:
            return {"function": "permit2Permit", "selector": selector, "args": [], "malformed": True}
        spender, amount = res
        return {"function": "permit2Permit", "selector": selector, "args": [spender, amount], "malformed": False}
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
    elif fn == "permit2Approve" and len(args) >= 3:
        spender, amt = args[1], args[2]          # NOTE: spender is arg[1], amount arg[2] for Permit2
        if amt >= _UNLIMITED_U160:
            flags.append({"code": "unlimited_approval", "severity": "HIGH",
                          "detail": f"{prefix}Permit2 approve() grants an effectively-unlimited allowance to "
                                    f"{spender} — a spender that turns malicious can drain that token."})
        elif amt >= _LARGE_APPROVAL:
            flags.append({"code": "large_approval", "severity": "MED",
                          "detail": f"{prefix}Permit2 approve() grants a very large allowance to {spender}; "
                                    "confirm it's intended."})
    elif fn == "permit2Permit" and len(args) >= 2:
        spender, amt = args[0], args[1]          # decoded form: [spender, worst-case amount]
        if amt >= _UNLIMITED_U160:
            flags.append({"code": "unlimited_approval", "severity": "HIGH",
                          "detail": f"{prefix}Permit2 permit() grants an effectively-unlimited allowance to "
                                    f"{spender} via a signed permit — a spender that turns malicious can drain that token."})
        elif amt >= _LARGE_APPROVAL:
            flags.append({"code": "large_approval", "severity": "MED",
                          "detail": f"{prefix}Permit2 permit() grants a very large allowance to {spender}; "
                                    "confirm it's intended."})
    elif fn == "permit" and len(args) >= 3:
        spender, value = args[1], args[2]
        if value >= _UNLIMITED_THRESHOLD:
            flags.append({"code": "unlimited_approval", "severity": "HIGH",
                          "detail": f"{prefix}permit() grants an effectively-unlimited allowance to {spender} via a "
                                    "signed permit — a spender that turns malicious can drain that token."})
        elif value >= _LARGE_APPROVAL:
            flags.append({"code": "large_approval", "severity": "MED",
                          "detail": f"{prefix}permit() grants a very large allowance to {spender}; confirm it's intended."})
    elif fn == "daiPermit" and len(args) >= 5 and args[4] is True:
        spender = args[1]
        flags.append({"code": "unlimited_approval", "severity": "HIGH",
                      "detail": f"{prefix}DAI permit() with allowed=true grants {spender} an effectively-unlimited "
                                "allowance via a signed permit — a spender that turns malicious can drain that token."})
    elif fn == "setApprovalForAll" and len(args) >= 2 and args[1] is True:
        flags.append({"code": "approval_for_all", "severity": "HIGH",
                      "detail": f"{prefix}setApprovalForAll grants {args[0]} control of EVERY token in this "
                                "collection — a common NFT-drain approval."})
    elif fn in ("transferFrom", "safeTransferFrom", "safeBatchTransferFrom", "permit2TransferFrom") and len(args) >= 2:
        asset = "tokens" if fn in ("transferFrom", "permit2TransferFrom") else "an NFT/token"
        flags.append({"code": "token_transfer_from", "severity": "HIGH",
                      "detail": f"{prefix}{fn} moves {asset} OUT of {args[0]} to {args[1]} — this is the call a "
                                "malicious spender uses to drain an approved wallet/collection. Confirm you intend it."})
    elif fn == "transfer" and len(args) >= 2 and args[1] >= _LARGE_APPROVAL:
        flags.append({"code": "large_transfer", "severity": "MED",
                      "detail": f"{prefix}transfer of a very large amount to {args[0]}; confirm the amount/recipient."})
    elif fn in ("upgradeTo", "upgradeToAndCall"):
        flags.append({"code": "proxy_upgrade", "severity": "HIGH",
                      "detail": f"{prefix}{fn}() repoints a proxy's logic to {args[0] if args else '?'} — this can "
                                "replace the contract's entire behavior. Only sign if you control that address."})
    return flags


def _multicall_inner(data):
    """Return the inner calldata strings of any known multicall variant, or None if not decodable."""
    s = _norm_hex(data) or ""
    types = _MULTICALL_VARIANTS.get("0x" + s[:8].lower())
    if not types:
        return None
    try:
        from eth_abi import decode as _abidecode
        decoded = _abidecode(types, bytes.fromhex(s[8:]))
        calls = decoded[-1]              # the bytes[] component is always last
        return ["0x" + c.hex() for c in calls]
    except Exception:
        return None


def _exec_inner(data):
    """Inner calldata of an ERC-4337 execute/executeBatch wrapper, or None if not one / undecodable.
    execute(to,value,data) -> one inner call; executeBatch(...) -> many (the bytes[] is last)."""
    s = _norm_hex(data) or ""
    selector = "0x" + s[:8].lower()
    try:
        from eth_abi import decode as _abidecode
        if selector in _EXEC_SINGLE:
            _to, _value, inner = _abidecode(_EXEC_SINGLE[selector], bytes.fromhex(s[8:]))
            return ["0x" + inner.hex()]
        if selector in _EXEC_BATCH:
            decoded = _abidecode(_EXEC_BATCH[selector], bytes.fromhex(s[8:]))
            return ["0x" + c.hex() for c in decoded[-1]]    # bytes[] is always last
    except Exception:
        return None
    return None


def _multisend_inner(data):
    """Inner calldata of a Gnosis Safe multiSend(bytes). The bytes arg is a PACKED list of
    (operation:1, to:20, value:32, dataLength:32, data:dataLength) records — not standard ABI."""
    s = _norm_hex(data) or ""
    if "0x" + s[:8].lower() != _MULTISEND:
        return None
    try:
        from eth_abi import decode as _abidecode
        (packed,) = _abidecode(["bytes"], bytes.fromhex(s[8:]))
    except Exception:
        return None
    calls, i, n = [], 0, len(packed)
    while i + 85 <= n:                                       # need at least the fixed header
        dlen = int.from_bytes(packed[i + 53:i + 85], "big")
        start, end = i + 85, i + 85 + dlen
        if end > n:                                          # truncated record — stop, don't guess
            break
        calls.append("0x" + packed[start:end].hex())
        i = end
    return calls


def _wrapper_inner(data, selector):
    """Inner calls for any wrapper selector, dispatched by family. Returns (inner_or_None, label)."""
    if selector in _MULTICALL_VARIANTS:
        return _multicall_inner(data), "(inside multicall) "
    if selector in _EXEC_SINGLE or selector in _EXEC_BATCH:
        return _exec_inner(data), "(inside execute) "
    return _multisend_inner(data), "(inside multiSend) "


def _ur_command_flags(cmd, inp, prefix, depth):
    """Flags for ONE Universal Router command + its raw ABI-tuple input. Only the Permit2 approval /
    transfer-from commands (and the recursive sub-plan) are dangerous; swaps/wrap/unwrap carry no such
    command and produce nothing — keeping benign swaps clean."""
    from eth_abi import decode as _abidecode
    label = prefix + "(inside Universal Router) "
    try:
        if cmd == _UR_PERMIT2_TRANSFER_FROM:
            _token, recipient, _amount = _abidecode(["address", "address", "uint160"], inp)
            return [{"code": "token_transfer_from", "severity": "HIGH",
                     "detail": f"{label}Permit2 transferFrom moves tokens OUT to {recipient} — the call a "
                               "malicious router script uses to drain an approved wallet. Confirm you intend it."}]
        if cmd == _UR_PERMIT2_TRANSFER_FROM_BATCH:
            (batch,) = _abidecode(["(address,address,uint160,address)[]"], inp)
            flags = []
            for _from, to, _amt, _tok in batch:
                flags.append({"code": "token_transfer_from", "severity": "HIGH",
                              "detail": f"{label}Permit2 transferFrom (batch) moves tokens OUT to {to} — the call a "
                                        "malicious router script uses to drain an approved wallet. Confirm you intend it."})
            return flags
        if cmd == _UR_PERMIT2_PERMIT:
            permit, _data = _abidecode(["((address,uint160,uint48,uint48),address,uint256)", "bytes"], inp)
            details, spender, _sig = permit            # details = (token, amount, expiration, nonce)
            return _ur_permit_flags(details[1], spender, label)
        if cmd == _UR_PERMIT2_PERMIT_BATCH:
            permit, _data = _abidecode(["((address,uint160,uint48,uint48)[],address,uint256)", "bytes"], inp)
            details_arr, spender, _sig = permit
            amount = max((d[1] for d in details_arr), default=0)
            return _ur_permit_flags(amount, spender, label)
        if cmd == _UR_EXECUTE_SUB_PLAN:
            if depth >= _MAX_MULTICALL_DEPTH:
                return [{"code": "deeply_nested_multicall", "severity": "HIGH",
                         "detail": f"{label}sub-plans nested deeper than {_MAX_MULTICALL_DEPTH} levels — "
                                   "abnormal obfuscation; treat as hostile and review before signing."}]
            sub_commands, sub_inputs = _abidecode(["bytes", "bytes[]"], inp)
            return _ur_process(sub_commands, sub_inputs, prefix, depth + 1)
    except Exception:
        return [{"code": "malformed_call", "severity": "MED",
                 "detail": f"{label}a Universal Router command's input couldn't be decoded — its real effect "
                           "can't be trusted; review before signing."}]
    return []


def _ur_permit_flags(amount, spender, label):
    if amount >= _UNLIMITED_U160:
        return [{"code": "unlimited_approval", "severity": "HIGH",
                 "detail": f"{label}Permit2 permit() grants an effectively-unlimited allowance to {spender} "
                           "via a signed permit — a spender that turns malicious can drain that token."}]
    if amount >= _LARGE_APPROVAL:
        return [{"code": "large_approval", "severity": "MED",
                 "detail": f"{label}Permit2 permit() grants a very large allowance to {spender}; confirm it's intended."}]
    return []


def _ur_process(commands, inputs, prefix, depth):
    """Walk a Universal Router command list, judging each command by its type byte + paired input."""
    flags = []
    for i, cmd_byte in enumerate(commands):
        cmd = cmd_byte & _UR_COMMAND_TYPE_MASK
        inp = inputs[i] if i < len(inputs) else b""
        flags.extend(_ur_command_flags(cmd, inp, prefix, depth))
    return flags


def _universal_router_flags(data, prefix="", depth=0):
    """Flags for a Universal Router execute() — decode (commands, inputs[, deadline]) and judge each
    command. Returns None if not a UR call (so callers fall through to normal decoding)."""
    s = _norm_hex(data) or ""
    types = _UR_EXEC.get("0x" + s[:8].lower())
    if not types:
        return None
    try:
        from eth_abi import decode as _abidecode
        decoded = _abidecode(types, bytes.fromhex(s[8:]))
    except Exception:
        return [{"code": "malformed_call", "severity": "MED",
                 "detail": f"{prefix}Universal Router calldata couldn't be decoded — its commands can't be "
                           "checked; review before signing."}]
    commands, inputs = decoded[0], decoded[1]
    return _ur_process(commands, inputs, prefix, depth)


def _collect_flags(data, prefix="", depth=0):
    """Risk flags for one call. If it WRAPS inner calls (multicall, ERC-4337 execute/executeBatch,
    Safe multiSend, Uniswap Universal Router), recurse into them so a drain hidden inside — even
    nested — is caught. Depth-capped against nesting bombs."""
    s = _norm_hex(data) or ""
    selector = "0x" + s[:8].lower()
    if selector in _UR_EXEC:
        return _universal_router_flags(data, prefix, depth)
    if selector in _WRAPPER_SELECTORS:
        if depth >= _MAX_MULTICALL_DEPTH:
            # Abnormally-deep nesting is not a legitimate pattern (real wrappers nest 1-2 deep) — it
            # is a strong obfuscation signal hiding calls we refuse to keep unwrapping. HIGH so the
            # hard stop (assert_safe) fires rather than waving it through with a soft advisory.
            return [{"code": "deeply_nested_multicall", "severity": "HIGH",
                     "detail": f"{prefix}call wrappers nested deeper than {_MAX_MULTICALL_DEPTH} levels — "
                               "this is not a normal pattern and hides calls that can't be inspected; "
                               "treat as hostile and do not sign without manual review."}]
        inner, label = _wrapper_inner(data, selector)
        if inner is None:
            return [{"code": "malformed_call", "severity": "MED",
                     "detail": f"{prefix}wrapped calldata couldn't be decoded — its inner calls can't be "
                               "checked; review before signing."}]
        flags = []
        for c in inner:
            flags.extend(_collect_flags(c, prefix=label, depth=depth + 1))
        return flags
    decoded = _decode(data)
    flags = _call_flags(decoded, prefix)
    # An unknown inner call is just as opaque as a top-level one — surface it (LOW), don't swallow it.
    if depth > 0 and decoded is not None and decoded.get("function") is None and s not in ("", "0x"):
        flags.append({"code": "opaque_calldata", "severity": "LOW",
                      "detail": f"{prefix}calls an unknown function ({decoded.get('selector')}); "
                                "can't tell what it does — review before signing."})
    return flags


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

    if selector in _WRAPPER_SELECTORS or selector in _UR_EXEC:
        flags.extend(_collect_flags(data))
        name = ("multicall" if selector in _MULTICALL_VARIANTS
                else "multiSend" if selector == _MULTISEND
                else "universalRouterExecute" if selector in _UR_EXEC else "execute")
        decoded = {"function": name, "selector": selector, "args": [], "malformed": False}
    else:
        flags.extend(_call_flags(decoded))
        if decoded is not None and decoded.get("function") is None and data not in ("0x", ""):
            flags.append({"code": "opaque_calldata", "severity": "LOW",
                          "detail": f"calldata calls an unknown function ({decoded.get('selector')}); "
                                    "can't tell what it does — review before signing."})

    # EIP-7702 account delegation (type-0x04 set-code): signing an authorization hands the delegate
    # contract control of the account — a current drainer vector disguised as a "wallet upgrade".
    auth_list = None
    for k, v in tx.items():
        if isinstance(k, str) and k.replace("_", "").lower() == "authorizationlist":
            auth_list = v
            break
    if isinstance(auth_list, dict):          # tolerate a single authorization, not just a list
        auth_list = [auth_list]
    if isinstance(auth_list, list) and auth_list:
        targets = [a.get("address") for a in auth_list if isinstance(a, dict)]
        flags.append({"code": "eip7702_delegation", "severity": "HIGH",
                      "detail": f"this transaction delegates account control via EIP-7702 to {targets} — the "
                                "delegate can then move your funds with no further approval. Only sign if you "
                                "set this up and trust that address (drainers disguise it as a 'wallet upgrade')."})

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
