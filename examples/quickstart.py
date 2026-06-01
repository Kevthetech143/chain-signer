"""chain-signer — 2-second offline quickstart.

Run it right after `pip install chain-signer`. No API key, no funds, no network needed:

    python quickstart.py

It makes a throwaway wallet, signs a message, proves the signature recovers to that wallet
(so the agent really holds the key — non-custodial), and round-trips an encrypted keystore.
"""
from eth_account import Account
from eth_account.messages import encode_defunct

from chain_signer import burner, sign_message, export_encrypted, load_encrypted


def demo(password="demo-pass"):
    """Run the full offline flow and return the results as a dict (used by tests + __main__)."""
    # 1) one-call fresh wallet — the agent owns the private key, nobody else ever sees it
    w = burner()

    # 2) sign a message and prove it recovers to OUR address (the key is real and ours)
    sig = sign_message(w, "hello from my agent")
    recovered = Account.recover_message(encode_defunct(text="hello from my agent"), signature=sig)

    # 3) store the key safely: encrypt to a keystore, then decrypt back to the same wallet
    keystore = export_encrypted(w, password)
    reloaded = load_encrypted(keystore, password)

    return {
        "address": w.address,
        "private_key": w.private_key,
        "signature": sig,
        "recovered": recovered,
        "keystore": keystore,
        "reloaded_address": reloaded.address,
    }


if __name__ == "__main__":
    d = demo()
    print("fresh wallet:        ", d["address"])
    print("signed a message ->  ", d["signature"][:20], "...")
    print("recovers to us?      ", d["recovered"] == d["address"])
    print("encrypted + reloaded?", d["reloaded_address"] == d["address"])
    print("\nYour agent just held a wallet and signed — no human, no custody, no network.")
