#!/bin/bash
# Push a one-line status to Kelvin on Telegram (used by the build cron each cycle).
# Reads the bot token from the vault; never prints it. Usage: notify.sh "message"
set -euo pipefail
TOKEN_FILE="$HOME/agents/global/tools/messaging/telegram-bot-polymarket.md"
TOKEN=$(grep -oE '[0-9]{6,}:[A-Za-z0-9_-]{30,}' "$TOKEN_FILE" | head -1)
CHAT_ID="5706754777"
MSG="${1:-(no message)}"
curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${CHAT_ID}" \
  --data-urlencode "text=${MSG}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('telegram_ok:', d.get('ok'), '' if d.get('ok') else d.get('description'))"
