"""Red tests — issues found by the stress-test sub-agents (2026-06-01). Security + x402 correctness."""
import pytest
from chain_signer import burner, sign_x402_payment
from chain_signer.mcp_stdio import handle

USDC = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
TO = "0x000000000000000000000000000000000000dEaD"


def test_mcp_never_echoes_a_bad_private_key_in_errors():
    # a malformed bitcoin WIF must NOT come back in the MCP tool error text (key-leak guard)
    bad = "KxBcdefghijkmnopqrstuvwxyz123456789ABCDEFGHJKLMNPQRSTUV"
    r = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "send", "arguments": {"chain": "bitcoin", "private_key": bad,
        "to": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT", "amount_btc": "0.001"}}})
    blob = str(r)
    assert bad not in blob, f"private key leaked into MCP output: {blob}"
    assert r["result"]["isError"], "bad key should be an error result"


def test_x402_rejects_non_bytes32_nonce():
    with pytest.raises(ValueError):
        sign_x402_payment(burner(), token=USDC, to=TO, value=1, valid_before=1893456000,
                          chain_id=84532, nonce="deadbeef")  # 4 bytes, not 32


def test_x402_value_signed_and_advertised_match_for_float():
    a = sign_x402_payment(burner(), token=USDC, to=TO, value=1000.0, valid_before=1893456000, chain_id=84532)
    assert a["authorization"]["value"] == "1000", f"advertised value must equal the signed int: {a['authorization']['value']}"


def test_balance_handles_non_dict_response():
    from chain_signer.balance import get_balance
    with pytest.raises(ValueError):
        get_balance(TO, fetch=lambda url: "rate limited, try later")  # non-dict, must not AttributeError
