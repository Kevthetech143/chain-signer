# Live end-to-end proof — chain-signer (Step 9)

## Proven live (real network, no funds moved)
- get_balance against the live Polygon chain via Etherscan v2: read 0x01F5404f...db46aD →
  POL 20.33609959930415, native USDC 0.0. The read path works end-to-end on the real chain. (2026-05-31)
- create_wallet: pure/local, already proven by unit tests (valid address, owner holds key).

## Remaining — needs Kelvin's go (touches real funds — binding stop gate)
The signing+broadcast paths (send / call_contract / swap) are unit-proven (signed tx recovers to owner).
To prove them LIVE with a real tx hash, the cleanest dogfood + the bonus transfer in one:
1. Tool creates wallet A (fresh).
2. Fund A with a TINY amount of POL from our existing wallet (one small real transfer; gas + a little).
3. Tool uses wallet A to send POL to wallet B (fresh) — this is the tool signing with its OWN key and
   broadcasting a real transaction. Capture the on-chain tx hash as proof.

Amounts: tiny (a few cents of POL). I will show both addresses + the tx hash before and after.
Broadcast path: Etherscan v2 proxy eth_sendRawTransaction or a public Polygon RPC (read truth stays Etherscan v2).

STATUS: AWAITING KELVIN'S GO for the real transfer. Cron holds here (no real funds without his explicit go).
