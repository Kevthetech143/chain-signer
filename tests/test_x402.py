"""Red tests — one-call x402 payment authorization (EIP-3009 TransferWithAuthorization).

The verified wedge: an agent paying an x402 API signs an EIP-3009 authorization (typed data) and
puts {signature, authorization} in the payment header. This pins sign_x402_payment(): it builds the
exact TransferWithAuthorization struct, signs it (EIP-712), and returns the header-ready payload, and
the signature recovers to the agent's wallet.
Spec: coinbase/x402 specs/schemes/exact/scheme_exact_evm.md (EIP-3009 + EIP-712).
"""
from eth_account import Account
from eth_account.messages import encode_typed_data

from chain_signer import burner, sign_x402_payment

USDC = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # Base Sepolia USDC
TO = "0x000000000000000000000000000000000000dEaD"
NONCE = "0x" + "11" * 32


def test_payload_shape_and_authorization_fields():
    w = burner()
    p = sign_x402_payment(w, token=USDC, to=TO, value=100000, valid_before=1893456000,
                          chain_id=84532, nonce=NONCE)
    assert p["signature"].startswith("0x") and len(p["signature"]) == 132
    a = p["authorization"]
    assert a["from"] == w.address and a["to"] == TO
    assert a["value"] == "100000"          # stringified uint
    assert a["validAfter"] == 0            # default
    assert a["validBefore"] == 1893456000
    assert a["nonce"] == NONCE


def test_signature_recovers_to_the_agent_wallet():
    w = burner()
    p = sign_x402_payment(w, token=USDC, to=TO, value=100000, valid_before=1893456000,
                          chain_id=84532, nonce=NONCE, token_name="USDC", token_version="2")
    domain = {"name": "USDC", "version": "2", "chainId": 84532, "verifyingContract": USDC}
    types = {"TransferWithAuthorization": [
        {"name": "from", "type": "address"}, {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"}, {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"}, {"name": "nonce", "type": "bytes32"}]}
    message = {"from": w.address, "to": TO, "value": 100000, "validAfter": 0,
               "validBefore": 1893456000, "nonce": bytes.fromhex(NONCE[2:])}
    recovered = Account.recover_message(
        encode_typed_data(domain_data=domain, message_types=types, message_data=message),
        signature=p["signature"])
    assert recovered == w.address


def test_random_nonce_when_omitted():
    w = burner()
    a = sign_x402_payment(w, token=USDC, to=TO, value=1, valid_before=1893456000, chain_id=84532)
    b = sign_x402_payment(w, token=USDC, to=TO, value=1, valid_before=1893456000, chain_id=84532)
    assert a["authorization"]["nonce"] != b["authorization"]["nonce"]  # random 32-byte each call
    assert len(a["authorization"]["nonce"]) == 66  # 0x + 64 hex
