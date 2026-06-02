#!/usr/bin/env bash
# Cadence gate for the E2E tester. Each cron fire runs this; it increments a counter and prints
# RUN on every 5th fire, else SKIP. Keeps the E2E (a full clean-install product test) periodic, not
# every cycle. Usage in a cron fire:
#   [ "$(bash tools/e2e_gate.sh)" = RUN ] && spawn a tester subagent to run tools/e2e_smoke.sh
C="$HOME/agents/chain-signer/.e2e_counter"
n=$(( $(cat "$C" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$C"
if [ $(( n % 5 )) -eq 0 ]; then echo "RUN"; else echo "SKIP ($n/5)"; fi
