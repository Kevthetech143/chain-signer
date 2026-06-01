"""Red tests — cross-chain bridge via LI.FI. Injected quote + broadcast: deterministic, no network/funds.

Crown check: the signed LI.FI transaction recovers to the OWNER's address.
"""
from eth_account import Account

from chain_signer import create_wallet
from chain_signer.bridge import get_bridge_quote, bridge_evm

USDC_POLY = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
USDC_ARB = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
LIFI_DIAMOND = "0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE"

QUOTE = {
    "tool": "across",
    "estimate": {"toAmount": "991195"},
    "transactionRequest": {"to": LIFI_DIAMOND, "data": "0xabcdef", "value": "0x0", "chainId": "0x89", "gasLimit": "0x7a120"},
}


def _quote_fetch():
    def f(url):
        f.url = url
        return QUOTE
    f.url = None
    return f


def _broadcast():
    def b(raw):
        b.raw = raw
        return "0x" + "bb" * 32
    b.raw = None
    return b


def test_quote_request_carries_route_integrator_and_fee():
    f = _quote_fetch()
    get_bridge_quote(137, 42161, USDC_POLY, USDC_ARB, 1_000_000,
                     "0x01F5404f0FFCEFBA097817cC3765556240db46aD", fee=0.001, fetch=f)
    u = f.url.lower()
    assert "fromchain=137" in u and "tochain=42161" in u, f"route missing: {f.url}"
    assert USDC_POLY.lower() in u and USDC_ARB.lower() in u, "tokens missing"
    assert "integrator=chain-signer" in u, "integrator missing"
    assert "fee=0.001" in u, "fee not attached"


def test_bridge_evm_signs_the_lifi_tx_and_recovers_to_owner():
    w = create_wallet("evm")
    b = _broadcast()
    res = bridge_evm(w, QUOTE, nonce=0, max_fee_per_gas=150 * 10**9, max_priority_fee_per_gas=35 * 10**9, broadcast=b)
    assert Account.recover_transaction(b.raw) == w.address, "bridge tx not signed by owner"
    assert res["hash"] == "0x" + "bb" * 32
    assert res["to"].lower() == LIFI_DIAMOND.lower(), "did not target the LI.FI router"


def test_bridge_result_never_contains_private_key():
    w = create_wallet("evm")
    res = bridge_evm(w, QUOTE, nonce=0, max_fee_per_gas=1, max_priority_fee_per_gas=1, broadcast=lambda r: "0xtid")
    assert w.private_key not in str(res), "private key leaked into bridge result"
