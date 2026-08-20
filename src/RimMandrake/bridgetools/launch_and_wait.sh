#!/usr/bin/env bash
# Launch RimWorld and wait until the BRIDGE of THIS run is up.
#
# 🔴 THE TRAP THIS EXISTS FOR: Player.log persists from the previous run until the
# new process truncates it, so grepping for "GABP server running standalone"
# matches the PREVIOUS session's line and returns instantly - before the new game
# has even started. Every wait loop must first see the log TRUNCATE.
set -u
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
MARK="GABP server running standalone"
BEFORE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
START=$(date +%s)

taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1 && sleep 3
cmd.exe /c start "" "steam://rungameid/294100" 2>/dev/null

# 1. wait for the log to be truncated or replaced by the new process
for i in $(seq 1 90); do
  sleep 2
  NOW=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
  [ "$NOW" -lt "$BEFORE" ] && break
  [ "$BEFORE" -eq 0 ] && [ "$NOW" -gt 0 ] && break
done
echo "log truncated after $(( $(date +%s)-START ))s (was $BEFORE, now $(stat -c %s "$LOG" 2>/dev/null))"

# 2. now the marker can only come from THIS run
for i in $(seq 1 120); do
  grep -q "$MARK" "$LOG" 2>/dev/null && { echo "BRIDGE UP after $(( $(date +%s)-START ))s"; exit 0; }
  tasklist.exe 2>/dev/null | grep -qi rimworld || { echo "PROCESS GONE after $(( $(date +%s)-START ))s"; exit 1; }
  sleep 2
done
echo "TIMEOUT after $(( $(date +%s)-START ))s"; exit 1
