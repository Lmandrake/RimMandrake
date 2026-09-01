#!/usr/bin/env bash
set -u
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
MARK="GABP server running standalone"
BEFORE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
START=$(date +%s)
taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1 && sleep 3
cmd.exe /c start "" "steam://rungameid/294100" 2>/dev/null
for i in $(seq 1 150); do
  sleep 2
  NOW=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
  [ "$NOW" -lt "$BEFORE" ] && break
  [ "$BEFORE" -eq 0 ] && [ "$NOW" -gt 0 ] && break
done
echo "log truncated after $(( $(date +%s)-START ))s"
for i in $(seq 1 1200); do
  grep -q "$MARK" "$LOG" 2>/dev/null && { echo "BRIDGE UP after $(( $(date +%s)-START ))s"; exit 0; }
  tasklist.exe 2>/dev/null | grep -qi rimworld || { echo "PROCESS GONE after $(( $(date +%s)-START ))s"; exit 1; }
  sleep 2
done
echo "TIMEOUT after $(( $(date +%s)-START ))s"; exit 1
