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


# --- Adversarial (2026-06-07): the zero-consideration net only SUMS amounts — it never checks WHO is
# paid. A drainer dodges it by making consideration NON-zero but routing every penny to THEMSELVES, so
# the victim (offerer) still nets nothing. Same evasion CLASS as the Permit2 approve->permit / witness
# swaps: a covered guard sidestepped by a variant that achieves the identical harm. ---

ATTACKER = "0x" + "ee" * 20


def test_seaport_consideration_all_to_third_party_is_high():
    """Victim offers an NFT; consideration is non-zero (dodges the all-zero net) but the ONLY recipient
    is the attacker — the offerer receives nothing. A real listing/bid always pays the offerer, so the
    offerer getting ZERO while assets leave is the giveaway drain in disguise. Must be HIGH."""
    consideration = [{"itemType": 0, "token": "0x" + "00" * 20, "identifierOrCriteria": 0,
                      "startAmount": 10 ** 18, "endAmount": 10 ** 18, "recipient": ATTACKER}]
    r = inspect_typed_data(_order([_OFFER_NFT], consideration))
    assert "seaport_consideration_not_to_offerer" in _codes(r)
    assert _sev(r, "seaport_consideration_not_to_offerer") == "HIGH"
    assert r["ok"] is False


def test_seaport_listing_with_fees_still_pays_offerer_not_flagged():
    """Legit listing with a marketplace fee + creator royalty: the SELLER is still paid a positive
    amount, the rest are fees to other recipients. Must NOT be flagged (no over-deny on normal splits)."""
    consideration = [
        {"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 95 * 10 ** 16, "endAmount": 95 * 10 ** 16, "recipient": SELLER},
        {"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 5 * 10 ** 16, "endAmount": 5 * 10 ** 16, "recipient": ATTACKER},
    ]
    r = inspect_typed_data(_order([_OFFER_NFT], consideration))
    assert "seaport_consideration_not_to_offerer" not in _codes(r)
    assert r["ok"] is True


def test_seaport_offerer_paid_zero_while_third_party_paid_is_high():
    """A subtle split: a token item to the offerer with amount 0 (looks like they're a recipient) but
    the real money goes to the attacker. The offerer's TAKE is zero, so this is still the drain."""
    consideration = [
        {"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 0, "endAmount": 0, "recipient": SELLER},
        {"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 10 ** 18, "endAmount": 10 ** 18, "recipient": ATTACKER},
    ]
    r = inspect_typed_data(_order([_OFFER_NFT], consideration))
    assert "seaport_consideration_not_to_offerer" in _codes(r)
    assert r["ok"] is False


def test_seaport_unreadable_offerer_does_not_falsely_flag_routing():
    """Conservative: if the offerer field is missing/unreadable we cannot claim 'the victim receives
    nothing', so the routing check must NOT fire (avoid crying wolf). A non-zero paid order with an
    unknown offerer is left to the zero-consideration net only."""
    consideration = [{"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 10 ** 18, "endAmount": 10 ** 18, "recipient": ATTACKER}]
    td = _order([_OFFER_NFT], consideration)
    td["message"].pop("offerer")
    r = inspect_typed_data(td)
    assert "seaport_consideration_not_to_offerer" not in _codes(r)
