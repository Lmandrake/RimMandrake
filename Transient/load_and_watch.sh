#!/usr/bin/env bash
set -u
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
bash src/RimMandrake/bridgetools/launch_and_wait.sh; echo "launch_and_wait exited $?"
# poll every 10 min for the JawaBench ready line (full drivable marker), up to 60 min
for i in 1 2 3 4 5 6; do
  if grep -q "\[JawaBench\] ready" "$LOG" 2>/dev/null; then
    echo "READY: $(grep -o '\[JawaBench\] ready[^"]*' "$LOG" | head -1)"
    grep -o '\[JawaBench\] context[^"]*' "$LOG" | head -1
    exit 0
  fi
  tasklist.exe 2>/dev/null | grep -qi rimworld || { echo "PROCESS DIED at poll $i"; exit 1; }
  echo "poll $i: still loading ($(date +%H:%M))"
  sleep 600
done
echo "NOT READY after 60+ minutes"; exit 1
