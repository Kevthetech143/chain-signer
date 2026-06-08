"""Adversarial angle (2026-06-08): the Seaport guard dispatched ONLY on primaryType
"OrderComponents". But Seaport (1.2+) also supports BULK ORDER signatures — a single EIP-712
signature over a merkle tree of orders (primaryType "BulkOrder", a `tree` of OrderComponents).
OpenSea uses it for bulk listings. So a drainer asks the agent to sign a "bulk listing" whose tree
contains the SAME zero-consideration / routed-consideration giveaway that the plain-order guard
catches — and it slipped through with ok=True, zero flags (empirically confirmed fail-OPEN).

Same evasion CLASS as the v0.5.16 Permit2 witness variants and v0.5.18 Seaport routed-consideration:
a covered giveaway hidden behind an uncovered wrapper. Fix: when primaryType is BulkOrder, flatten
the tree and run the SAME _seaport_flags on every order-shaped node. Non-noisy by reuse — padding /
empty-offer tree leaves and normal listings (offerer paid) stay clean, exactly as a plain order does.
"""
from chain_signer.sig_inspect import inspect_typed_data


def _codes(r):
    return {f["code"] for f in r["risk_flags"]}


NFT = "0x" + "11" * 20
SELLER = "0x" + "aa" * 20
ATTACKER = "0x" + "ee" * 20
_OFFER_NFT = {"itemType": 2, "token": NFT, "identifierOrCriteria": 42, "startAmount": 1, "endAmount": 1}


def _order(consideration):
    return {"offerer": SELLER, "offer": [_OFFER_NFT], "consideration": consideration,
            "startTime": 0, "endTime": 9999999999, "salt": 1, "counter": 0}


_GIVEAWAY = _order([])
_ROUTED = _order([{"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 10 ** 18,
                   "endAmount": 10 ** 18, "recipient": ATTACKER}])
_LEGIT = _order([{"itemType": 0, "token": "0x" + "00" * 20, "startAmount": 10 ** 18,
                  "endAmount": 10 ** 18, "recipient": SELLER}])


def _bulk(tree):
    return {"primaryType": "BulkOrder", "domain": {"name": "Seaport", "version": "1.6"},
            "message": {"tree": tree}}


def test_bulkorder_zero_consideration_is_high():
    r = inspect_typed_data(_bulk([_GIVEAWAY, _LEGIT]))
    assert "seaport_zero_consideration" in _codes(r)
    assert r["ok"] is False


def test_bulkorder_routed_consideration_is_high():
    r = inspect_typed_data(_bulk([_LEGIT, _ROUTED]))
    assert "seaport_consideration_not_to_offerer" in _codes(r)
    assert r["ok"] is False


def test_bulkorder_nested_tree_is_caught():
    # Seaport bulk trees are nested fixed-size arrays — the giveaway can sit one layer down.
    r = inspect_typed_data(_bulk([[_LEGIT, _GIVEAWAY], [_LEGIT, _LEGIT]]))
    assert "seaport_zero_consideration" in _codes(r)
    assert r["ok"] is False


def test_bulkorder_case_insensitive():
    td = _bulk([_GIVEAWAY]) | {"primaryType": "  bulkOrder "}
    assert "seaport_zero_consideration" in _codes(inspect_typed_data(td))


def test_bulkorder_all_legit_listings_not_flagged():
    r = inspect_typed_data(_bulk([_LEGIT, _LEGIT, _LEGIT]))
    assert "seaport_zero_consideration" not in _codes(r)
    assert "seaport_consideration_not_to_offerer" not in _codes(r)
    assert r["ok"] is True


def test_bulkorder_empty_offer_padding_not_flagged():
    # Bulk trees are padded to a power of two with empty (zeroed) orders — no offer => nothing to give
    # away => must not false-positive.
    padding = {"offerer": "0x" + "00" * 20, "offer": [], "consideration": []}
    r = inspect_typed_data(_bulk([_LEGIT, padding, padding, padding]))
    assert r["ok"] is True


def test_bulkorder_malformed_does_not_crash():
    assert isinstance(inspect_typed_data(_bulk("not-a-list")), dict)
    assert isinstance(inspect_typed_data(_bulk(None)), dict)
    assert isinstance(inspect_typed_data({"primaryType": "BulkOrder", "message": None}), dict)
