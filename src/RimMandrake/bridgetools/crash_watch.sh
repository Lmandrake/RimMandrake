#!/usr/bin/env bash
# Passive crash watcher for RimWorldWin64.exe, started 2026-09-05 during
# NINEFOLD_DEBUG_GAME_READY_CRASH_1's post-reboot retest. Owner's ruling:
# proceed as though the full 596-mod list is fine; if it crashes anyway,
# capture everything useful about HOW, since nobody has ever caught this
# with real instrumentation running before.
#
# Runs until RimWorldWin64.exe disappears, then writes a timestamped
# crash report (RSS trend tail, Player.log tail, Windows Event Viewer
# Application/System entries near the death instant) and exits. Does
# nothing while the game is running beyond sampling RSS every 5s.
set -u
HERE="/mnt/d/Luke/dev/Rimworld/Transient"
MEMLOG="$HERE/rimworld_mem_watch_2026-09-05.log"
PLOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"

echo "crash_watch started $(date -u +%FT%TZ)" >> "$MEMLOG"

while true; do
  LINE=$(tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe" /FO CSV 2>/dev/null | tail -1)
  if ! echo "$LINE" | grep -q "RimWorldWin64"; then
    DEATH=$(date -u +%FT%TZ)
    REPORT="$HERE/crash_report_$(date +%Y%m%d_%H%M%S).md"
    {
      echo "# Crash report — RimWorldWin64.exe disappeared"
      echo "detected: $DEATH"
      echo
      echo "## RSS trend, last 40 samples before death"
      tail -40 "$MEMLOG"
      echo
      echo "## Player.log, last 60 lines"
      tail -60 "$PLOG" 2>/dev/null
      echo
      echo "## Windows Event Viewer, Application 1000/1001 (last 5)"
      wevtutil.exe qe Application /q:"*[System[(EventID=1000 or EventID=1001)]]" /c:5 /rd:true /f:text 2>&1
      echo
      echo "## Windows Event Viewer, System 41/1074/2004/6008 (last 5)"
      wevtutil.exe qe System /q:"*[System[(EventID=41 or EventID=1074 or EventID=2004 or EventID=6008)]]" /c:5 /rd:true /f:text 2>&1
      echo
      echo "## free -h at detection"
      free -h
    } > "$REPORT"
    echo "$DEATH DEAD -- report at $REPORT" >> "$MEMLOG"
    exit 0
  fi
  echo "$(date +%s) $LINE" >> "$MEMLOG"
  sleep 5
done
