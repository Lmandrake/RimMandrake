#!/usr/bin/env bash
set -u
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
BEFORE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
START=$(date +%s)
taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1
sleep 3
cmd.exe /c start "" "steam://rungameid/294100" 2>/dev/null
echo "launched at $(date -u +%FT%TZ)"

for i in $(seq 1 90); do
  sleep 2
  NOW=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
  [ "$NOW" -lt "$BEFORE" ] && { echo "log truncated after $(( $(date +%s)-START ))s"; break; }
  [ "$BEFORE" -eq 0 ] && [ "$NOW" -gt 0 ] && { echo "log created after $(( $(date +%s)-START ))s"; break; }
done

for i in $(seq 1 600); do
  if grep -q "Bridge token:" "$LOG" 2>/dev/null; then
    echo "BRIDGE UP after $(( $(date +%s)-START ))s"
    exit 0
  fi
  if grep -q "Recovered from incompatible or corrupted mods\|Caught exception while loading play data" "$LOG" 2>/dev/null; then
    echo "LOAD ABORTED after $(( $(date +%s)-START ))s"
    exit 2
  fi
  tasklist.exe 2>/dev/null | grep -qi rimworld || { echo "PROCESS GONE after $(( $(date +%s)-START ))s"; exit 1; }
  sleep 5
done
echo "TIMEOUT after $(( $(date +%s)-START ))s"
exit 3
