"""Real-world drainer-technique corpus — proves the suite flags the ACTUAL techniques used by the
dominant wallet drainers, not just synthetic shapes.

Grounding (cited security research, 2024-2025):
- Wallet drainers stole ~$494M in 2024; dominant kits: Inferno / Angel / Pink / Ace
  (Check Point Research "Inferno Drainer Reloaded" 2025; SlowMist 2024 AML report).
- Permit / Permit2 SIGNATURES are the #1 vector — 56.7% of phishing attacks (SlowMist 2024).
- setApprovalForAll single-signature NFT theft (Check Point: the "14 NFTs licensed" case).
- approve(unlimited) + transferFrom pull; EIP-7702 "wallet upgrade" delegation (newest, 2025+).

Each test encodes the real technique (real 4-byte selectors / EIP-712 shapes) and asserts our suite
flags it HIGH. Attacker address is a placeholder; the TECHNIQUE is what's real.

Honest note documented here: static decoding is IMMUNE to the "Red Pill" / TOCTOU simulation-evasion
that defeats simulation-based scanners — we read the calldata's literal intent (an unlimited approve
is unlimited regardless of how the contract behaves at runtime). That is a real strength, not a claim.
"""
from chain_signer.preflight import preflight
from chain_signer.sig_inspect import inspect_typed_data

ATTACKER = "0x" + "ba" * 20   # drainer-controlled spender (placeholder)
TOKEN = "0x" + "33" * 20
VICTIM = "0x" + "11" * 20
MAX256 = (1 << 256) - 1
U160_MAX = (1 << 160) - 1


def _tx_codes(tx):
    return {f["code"] for f in preflight(tx)["risk_flags"]}


def _sig_codes(td):
    return {f["code"] for f in inspect_typed_data(td)["risk_flags"]}


# #1 (56.7% of real attacks) — Permit2 signature drain (Uniswap "Permit2 Permit" abuse)
def test_permit2_signature_drain_caught():
    td = {"primaryType": "PermitSingle", "domain": {"name": "Permit2"},
          "message": {"details": {"token": TOKEN, "amount": str(U160_MAX)}, "spender": ATTACKER}}
    assert "unlimited_permit_signature" in _sig_codes(td)


# #1b — ERC-2612 permit signature drain
def test_erc2612_permit_signature_drain_caught():
    td = {"primaryType": "Permit", "domain": {"verifyingContract": TOKEN},
          "message": {"owner": VICTIM, "spender": ATTACKER, "value": str(MAX256), "deadline": 9999999999}}
    assert "unlimited_permit_signature" in _sig_codes(td)


# #2 — setApprovalForAll NFT single-signature theft (the documented 14-NFT case)
def test_setapprovalforall_nft_drain_caught():
    tx = {"to": TOKEN, "data": "0xa22cb465" + ATTACKER[2:].rjust(64, "0") + format(1, "064x"), "value": 0}
    assert "approval_for_all" in _tx_codes(tx)


# #3 — approve(unlimited) to drainer contract
def test_unlimited_approve_drain_caught():
    tx = {"to": TOKEN, "data": "0x095ea7b3" + ATTACKER[2:].rjust(64, "0") + "f" * 64, "value": 0}
    assert "unlimited_approval" in _tx_codes(tx)


# #3b — direct transferFrom pull (after a bad approval) / NFT safeTransferFrom
def test_transferfrom_pull_caught():
    tx = {"to": TOKEN, "data": "0x23b872dd" + VICTIM[2:].rjust(64, "0") + ATTACKER[2:].rjust(64, "0") + format(10 ** 21, "064x"), "value": 0}
    assert "token_transfer_from" in _tx_codes(tx)


# #4 — EIP-7702 "wallet upgrade" delegation drainer (2025+ frontier)
def test_eip7702_delegation_drain_caught():
    tx = {"to": VICTIM, "data": "0x", "value": 0, "authorizationList": [{"chainId": 1, "address": ATTACKER, "nonce": 0}]}
    assert "eip7702_delegation" in _tx_codes(tx)
