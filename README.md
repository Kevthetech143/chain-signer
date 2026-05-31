# chain-signer

A non-custodial, multi-chain transaction tool for AI agents. The agent holds its own key and
signs + posts transactions directly — no MetaMask, no browser. Every swap carries a tiny built-in
fee (0.1%) routed to a collector address; the tool never takes custody of anyone's funds.

Status: EVM (Polygon) first. Solana + Bitcoin are phase 1.5; Klever is phase 2.

## Install
```
pip install -e .            # needs Python 3.10+, web3, eth-account, eth-abi, eth-utils
export ETHERSCAN_API_KEY=...           # for balance reads (Etherscan v2)
export CHAIN_SIGNER_FEE_RECIPIENT=0x...# the address that collects swap fees (optional)
```

## Library usage
```python
from chain_signer import create_wallet
from chain_signer.balance import get_balance
from chain_signer.tx import send, call_contract
from chain_signer.swap import swap

w = create_wallet("evm")          # the agent owns w.private_key (keep it safe)
bal = get_balance(w.address)      # live balance from the chain

# All signing calls take live nonce/gas + a `broadcast(raw_hex)` function that posts the tx.
res = send(w, "0x...recipient", 1000, nonce=n, max_fee_per_gas=f, max_priority_fee_per_gas=p,
           chain_id=137, broadcast=my_broadcaster)

# Interact with any app/contract (e.g. an ERC-20 transfer):
call_contract(w, "0x...token", "transfer(address,uint256)", ["0x...to", 1000],
              nonce=n, max_fee_per_gas=f, max_priority_fee_per_gas=p, chain_id=137, broadcast=my_broadcaster)

# Swap with the built-in fee:
swap(w, "0x...sell", "0x...buy", 1_000_000, fee_recipient="0x...collector",
     nonce=n, max_fee_per_gas=f, max_priority_fee_per_gas=p, chain_id=137,
     fetch=my_fetch, broadcast=my_broadcaster)
```

## Tool surface (for any AI / MCP / CLI)
`chain_signer.mcp_server` exposes `list_tools()` and `call_tool(name, arguments)` covering all five
functions. The CLI wraps it:
```
python -m chain_signer list
python -m chain_signer call create_wallet '{"chain":"evm"}'
```

## Non-custodial guarantee
The private key is generated/loaded locally, used only to sign, and never logged, returned, or
stored by this library. `create_wallet` returns the key to its owner once; after that the owner keeps it.

## Notes
- Balances are read from the Etherscan v2 indexer (authoritative), never a free public RPC.
- Swap fee params (0x integrator fee) are confirmed against live 0x docs at the live fork-proof step.
