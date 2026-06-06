"""Adversarial angle (2026-06-06): the signature inspector covered the whole PERMIT family
(ERC-2612, DAI, Permit2 allowance + SignatureTransfer) but NOT Seaport order signatures — the
dominant NFT-drain phishing vector.

The scam: a "claim/mint" site asks the agent to SIGN an EIP-712 Seaport order (primaryType
"OrderComponents") whose `offer` contains the agent's valuable NFT/tokens and whose `consideration`
is EMPTY or all-zero — i.e. give the asset away for nothing. The agent signs it like a harmless
login; the attacker submits it and takes the NFT. This is the off-chain sibling of setApprovalForAll
and exactly what inspect_typed_data exists to catch.

Detection is deliberately CONSERVATIVE to avoid crying wolf on legitimate listings: a normal listing
always has non-zero consideration paid to the seller, so we flag HIGH only when the order OFFERS
assets but the consideration is empty / all-zero (an unambiguous giveaway). A normal-priced listing
must NOT be flagged.
"""
from chain_signer.sig_inspect import inspect_typed_data


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


def _sev(r, code):
    return next(f["severity"] for f in r["risk_flags"] if f["code"] == code)


NFT = "0x" + "11" * 20
SELLER = "0x" + "aa" * 20

# Seaport offer item (the NFT being given): itemType 2 = ERC721
_OFFER_NFT = {"itemType": 2, "token": NFT, "identifierOrCriteria": 42, "startAmount": 1, "endAmount": 1}


def _order(offer, consideration):
    return {
        "primaryType": "OrderComponents",
        "domain": {"name": "Seaport", "version": "1.6", "verifyingContract": "0x" + "00" * 19 + "01"},
        "message": {
            "offerer": SELLER,
            "offer": offer,
            "consideration": consideration,
            "startTime": 0, "endTime": 9999999999, "salt": 1, "counter": 0,
        },
    }


def test_seaport_empty_consideration_is_high():
    r = inspect_typed_data(_order([_OFFER_NFT], []))
    assert "seaport_zero_consideration" in _codes(r)
    assert _sev(r, "seaport_zero_consideration") == "HIGH"
    assert r["ok"] is False


def test_seaport_all_zero_consideration_is_high():
    consideration = [{"itemType": 0, "token": "0x" + "00" * 20, "identifierOrCriteria": 0,
                      "startAmount": 0, "endAmount": 0, "recipient": SELLER}]
    r = inspect_typed_data(_order([_OFFER_NFT], consideration))
    assert "seaport_zero_consideration" in _codes(r)
    assert r["ok"] is False


def test_seaport_normal_listing_not_flagged():
    # legit: offer the NFT, receive 1 ETH — must NOT trip the giveaway flag
    consideration = [{"itemType": 0, "token": "0x" + "00" * 20, "identifierOrCriteria": 0,
                      "startAmount": 10 ** 18, "endAmount": 10 ** 18, "recipient": SELLER}]
    r = inspect_typed_data(_order([_OFFER_NFT], consideration))
    assert "seaport_zero_consideration" not in _codes(r)
    assert r["ok"] is True


def test_seaport_primarytype_case_insensitive():
    r = inspect_typed_data(_order([_OFFER_NFT], []) | {"primaryType": "  orderComponents "})
    assert "seaport_zero_consideration" in _codes(r)


def test_seaport_no_offer_not_flagged():
    # nothing offered -> nothing to give away; do not flag
    r = inspect_typed_data(_order([], []))
    assert "seaport_zero_consideration" not in _codes(r)


def test_seaport_malformed_does_not_crash():
    bad = {"primaryType": "OrderComponents", "message": {"offer": "not-a-list", "consideration": None}}
    r = inspect_typed_data(bad)            # must not raise
    assert isinstance(r, dict) and "risk_flags" in r
