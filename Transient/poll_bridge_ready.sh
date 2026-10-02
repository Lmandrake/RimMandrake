#!/bin/bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
DEADLINE=$(( $(date +%s) + 1800 ))
while [ $(date +%s) -lt $DEADLINE ]; do
  if [ -f "$LOG" ]; then
    if grep -q "Bridge token:" "$LOG" 2>/dev/null; then
      echo "READY: Bridge token found at $(date)"
      grep "Bridge token:" "$LOG" | tail -1
      exit 0
    fi
    if grep -q "Recovered from incompatible or corrupted mods" "$LOG" 2>/dev/null; then
      echo "ABORTED: Recovered from incompatible or corrupted mods errors at $(date)"
      exit 1
    fi
    if grep -q "Caught exception while loading play data" "$LOG" 2>/dev/null; then
      echo "ABORTED: Caught exception while loading play data at $(date)"
      exit 1
    fi
  fi
  sleep 15
done
echo "TIMEOUT after 30 minutes waiting for Bridge token"
exit 2
