#!/bin/zsh
cd "$(dirname "$0")"

if [ -f bot.pid ]; then
  PID=$(cat bot.pid)
  echo "🛑 Stopping bot PID: $PID"
  kill -INT "$PID" 2>/dev/null
  sleep 1
  kill -9 "$PID" 2>/dev/null
  rm -f bot.pid
  echo "✅ Bot stopped"
else
  echo "ℹ️ bot.pid not found — bot may be already stopped"
fi

