#!/bin/bash
# Double-click to start the Job Office and open it in your default browser.
cd "$(dirname "$0")"
PORT=8790
if ! lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  PORT=$PORT nohup python3 server.py >/tmp/job_office.log 2>&1 &
  sleep 1
fi
open "http://localhost:$PORT"
echo "Job office is running at http://localhost:$PORT (close this window any time)."
