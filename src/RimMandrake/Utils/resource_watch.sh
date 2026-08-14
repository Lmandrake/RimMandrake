#!/usr/bin/env bash
# resource_watch.sh — sample WSL + Windows + GPU state so the NEXT WSL death has evidence.
#
# Why this exists: on 2026-08-14 a "WSL crash" was investigated after the fact and
# every diagnostic had already been erased — dmesg was 5 minutes old because the
# recovery reboot cleared it, and Windows had no bugcheck to explain (Minidump
# empty since Jul 16, zero Kernel-Power 41). The failure is real but leaves no
# trace, so it has to be caught live. The LAST LINE written before the log stops
# is the measurement; the script does not need to survive the event itself.
#
# Usage:  ./resource_watch.sh [interval_seconds]      (default 15)
# Output: observed/resource_watch/watch_<stamp>.csv   (gitignored — it is cache)
#         observed/resource_watch/watch_<stamp>.dmesg (new kernel lines only)
# Stop:   Ctrl-C, or kill the background job.

set -uo pipefail

REPO=/mnt/d/Luke/dev/Rimworld
OUTDIR="$REPO/observed/resource_watch"
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
INTERVAL="${1:-15}"

mkdir -p "$OUTDIR"
STAMP=$(date +%Y%m%d_%H%M%S)
CSV="$OUTDIR/watch_$STAMP.csv"
DMESG="$OUTDIR/watch_$STAMP.dmesg"

# One PowerShell call per tick returns every Windows-side number as one CSV row.
# Batched deliberately: each interop launch costs ~0.7s, so four calls would cost
# more than the sample is worth.
read -r -d '' PSQ <<'EOF'
$os = Get-CimInstance Win32_OperatingSystem
$p  = Get-Process | Group-Object ProcessName -AsHashTable -AsString
function ws($n) { if ($p[$n]) { [math]::Round((($p[$n] | Measure-Object WorkingSet64 -Sum).Sum)/1MB,0) } else { 0 } }
$vals = @(
  [math]::Round($os.FreePhysicalMemory/1KB,0),      # free physical MB
  [math]::Round(($os.TotalVirtualMemorySize - $os.FreeVirtualMemory)/1KB,0),  # commit used MB
  [math]::Round($os.TotalVirtualMemorySize/1KB,0),  # commit limit MB
  (ws 'vmmemWSL'), (ws 'RimWorldWin64'), (ws 'Steam'), (ws 'dwm'), (ws 'Memory Compression')
)
$vals -join ','
EOF

# Header, plus a provenance line: distinguishes "WSL restarted" from "Windows rebooted"
# when reading the log back — without it the two are indistinguishable after the fact.
{
  echo "# resource_watch $STAMP  interval=${INTERVAL}s"
  echo "# wsl_boot=$(date -d "@$(( $(date +%s) - $(cut -d. -f1 /proc/uptime) ))" -Iseconds)"
  echo "# win_boot=$($PS -NoProfile -Command "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('o')" 2>/dev/null | tr -d '\r')"
  echo "ts,wsl_avail_mb,wsl_claude_rss_mb,wsl_nproc_claude,load1,win_free_mb,win_commit_mb,win_commit_limit_mb,vmmemwsl_mb,rimworld_mb,steam_mb,dwm_mb,memcomp_mb,gpu_used_mib,gpu_total_mib,gpu_util_pct"
} >> "$CSV"

echo "resource_watch: $CSV  (interval ${INTERVAL}s, Ctrl-C to stop)"
LAST_DMESG=$(dmesg 2>/dev/null | wc -l)

while true; do
  TS=$(date -Iseconds)

  # --- WSL side (cheap, read straight from /proc) ---
  AVAIL=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  CLAUDE_RSS=$(ps -eo rss,comm --no-headers | awk '$2=="claude"{s+=$1} END{print int(s/1024)+0}')
  CLAUDE_N=$(pgrep -xc claude 2>/dev/null || echo 0)
  LOAD1=$(cut -d' ' -f1 /proc/loadavg)

  # --- GPU (WSL sees the host GPU through /dev/dxg) ---
  GPU=$(nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu \
        --format=csv,noheader,nounits 2>/dev/null | tr -d ' ' | head -1)
  [ -z "$GPU" ] && GPU=",,"

  # --- Windows side ---
  WIN=$($PS -NoProfile -Command "$PSQ" 2>/dev/null | tr -d '\r' | tail -1)
  [ -z "$WIN" ] && WIN=",,,,,,,"

  echo "$TS,$AVAIL,$CLAUDE_RSS,$CLAUDE_N,$LOAD1,$WIN,$GPU" >> "$CSV"

  # --- new kernel messages only (an OOM kill or a dxg fault lands here) ---
  NOW_DMESG=$(dmesg 2>/dev/null | wc -l)
  if [ "$NOW_DMESG" -gt "$LAST_DMESG" ]; then
    { echo "=== $TS ==="; dmesg | tail -n $(( NOW_DMESG - LAST_DMESG )); } >> "$DMESG"
    LAST_DMESG=$NOW_DMESG
  fi

  sleep "$INTERVAL"
done
