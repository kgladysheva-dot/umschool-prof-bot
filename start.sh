#!/bin/zsh
cd "$(dirname "$0")"

source venv/bin/activate
export BOT_TOKEN="8025638640:AAGst-o6_e6cFAn0dBSu1IHez5hA3xr2JIQ"

nohup python3 bot.py > bot.log 2>&1 & echo $! > bot.pid
echo "✅ Bot started. PID: $(cat bot.pid)"
echo "📄 Logs: tail -f bot.log"

