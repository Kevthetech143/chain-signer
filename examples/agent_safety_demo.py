"""Agent-security suite — see all three guards stop real attacks in 2 seconds.

Offline, no keys, no network. Run:  python examples/agent_safety_demo.py

The pitch in one file: an AI agent is about to (1) sign a draining transaction, (2) sign a
permit-phishing message, (3) call a tool outside policy. Each guard catches it BEFORE harm.
"""
from chain_signer import preflight, inspect_typed_data, check_action

SPENDER = "0x" + "22" * 20   # pretend-attacker
TOKEN = "0x" + "33" * 20


def show(title, report, ok_key="ok"):
    bad = report[ok_key] is False if ok_key in report else not report.get("allowed", True)
    flags = report.get("risk_flags") or report.get("violations") or []
    mark = "🛑 BLOCKED" if bad else "✅ ok"
    print(f"\n{title}\n  {mark}")
    for f in flags:
        print(f"   - [{f.get('severity','-')}] {f.get('code')}: {f.get('detail','')[:88]}")


print("=" * 70)
print("chain-signer agent-security suite — three guards vs three real attacks")
print("=" * 70)

# 1) Transaction guard — an unlimited-allowance approve() (the classic drain setup)
drain_tx = {"to": TOKEN, "data": "0x095ea7b3" + SPENDER[2:].rjust(64, "0") + "f" * 64, "value": 0}
show("1) preflight(tx): agent about to sign an UNLIMITED approval", preflight(drain_tx))

# 2) Signature guard — an ERC-2612 permit signature granting unlimited allowance
permit = {"primaryType": "Permit", "domain": {"verifyingContract": TOKEN},
          "message": {"spender": SPENDER, "value": str((1 << 256) - 1), "deadline": 9999999999}}
show("2) inspect_typed_data(td): agent about to SIGN a permit-phishing message", inspect_typed_data(permit))

# 3) Action guard — a tool call that breaks policy (sends more than allowed, to a stranger)
policy = {"max_value_wei": 10 ** 18, "allow_recipients": ["0x" + "11" * 20]}
action = {"tool": "send", "args": {"to": SPENDER, "value_wei": 50 * 10 ** 18}}
show("3) check_action(action, policy): agent about to act outside policy", action_gate := check_action(action, policy), ok_key="allowed")

print("\n" + "=" * 70)
print("All three caught before signing/acting. A guard, not a guarantee — pair it with")
print("your wallet + identity stack. pip install chain-signer")
print("=" * 70)
