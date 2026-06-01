"""Read on-chain balances from the LIVE chain (read-only, non-custodial).

Uses the Etherscan v2 API (authoritative indexer) — never a free public RPC, which can
return false zeros. The `fetch` dependency is injectable so the logic is unit-testable
without a network call. The API key is read from the ETHERSCAN_API_KEY env var — never hardcoded.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SUPPORTED_CHAINS = ("evm", "solana")
CHAIN_IDS = {"evm": 137}  # Polygon mainnet
ETHERSCAN_V2_BASE = "https://api.etherscan.io/v2/api"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"


def _default_fetch(url: str) -> dict:
    with urlopen(url, timeout=20) as resp:  # noqa: S310 (https only, built URL)
        return json.load(resp)


def _default_solana_rpc(method, params, url=SOLANA_RPC):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=20) as resp:  # noqa: S310
        return json.load(resp).get("result")


def _resolve_address(target) -> str:
    """Accept a Wallet (has .address) or a plain address string."""
    return str(getattr(target, "address", target))


def get_solana_balance(target, *, rpc=None):
    """Return native SOL balance (read-only) via Solana JSON-RPC getBalance."""
    res = (rpc or _default_solana_rpc)("getBalance", [_resolve_address(target)])
    return res["value"] / 1e9


def get_balance(target, token=None, *, chain="evm", decimals=18, fetch=None, rpc=None):
    """Return the balance of `target` (a Wallet or address) in human units.

    EVM: token=None reads native (POL); a token address reads that ERC-20. Solana: native SOL.
    """
    if chain not in SUPPORTED_CHAINS:
        raise ValueError(
            f"unsupported chain {chain!r}; supported: {', '.join(SUPPORTED_CHAINS)}"
        )
    if chain == "solana":
        return get_solana_balance(target, rpc=rpc)
    fetch = fetch or _default_fetch
    params = {
        "chainid": CHAIN_IDS[chain],
        "module": "account",
        "address": _resolve_address(target),
        "tag": "latest",
        "apikey": os.environ.get("ETHERSCAN_API_KEY", ""),
    }
    if token is None:
        params["action"] = "balance"
    else:
        params["action"] = "tokenbalance"
        params["contractaddress"] = token
    url = ETHERSCAN_V2_BASE + "?" + urlencode(params)
    data = fetch(url)
    return int(data["result"]) / (10 ** decimals)
