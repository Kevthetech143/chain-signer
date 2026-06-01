"""Red tests — Solana balance via chain dispatch (Solana JSON-RPC), + EVM regression guard."""
import pytest

from chain_signer import create_wallet
from chain_signer.balance import get_balance


def test_solana_get_balance_converts_lamports_to_sol():
    def rpc(method, params):
        rpc.method, rpc.addr = method, params[0]
        return {"value": 1_500_000_000}  # 1.5 SOL in lamports
    rpc.method = rpc.addr = None
    w = create_wallet("solana")
    bal = get_balance(w, chain="solana", rpc=rpc)
    assert bal == pytest.approx(1.5), f"lamports not converted by 1e9: {bal}"
    assert rpc.method == "getBalance", "did not call getBalance"
    assert rpc.addr == w.address, "queried the wrong address"


def test_solana_zero_balance_reads_clean():
    bal = get_balance("So11111111111111111111111111111111111111112", chain="solana", rpc=lambda m, p: {"value": 0})
    assert bal == 0


def test_evm_balance_unaffected_by_dispatch():
    def fetch(url):
        return {"status": "1", "result": "9854633000000000000"}
    bal = get_balance("0x01F5404f0FFCEFBA097817cC3765556240db46aD", fetch=fetch)
    assert bal == pytest.approx(9.854633)
