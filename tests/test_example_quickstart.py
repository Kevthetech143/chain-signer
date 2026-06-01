"""Red test — the zero-setup example must actually run and prove the non-custodial claim.

A developer's FIRST run after `pip install` shouldn't need an API key, funds, or a network.
examples/quickstart.py is that 2-second "it works" moment: make a wallet, sign a message, prove
the signature recovers to the wallet (the key is real and ours), and round-trip an encrypted
keystore. This test pins that the example's demo() does all of it, offline.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))


def test_quickstart_demo_runs_offline_and_proves_ownership():
    import quickstart
    d = quickstart.demo()
    # made a real wallet
    assert d["address"].startswith("0x") and len(d["address"]) == 42
    # the signature recovers to the signer -> the agent genuinely holds the key (non-custodial)
    assert d["recovered"] == d["address"]
    # encrypted keystore round-trips back to the SAME wallet
    assert d["reloaded_address"] == d["address"]
    # encrypted blob is not the plaintext key
    assert d["private_key"] not in str(d["keystore"])
