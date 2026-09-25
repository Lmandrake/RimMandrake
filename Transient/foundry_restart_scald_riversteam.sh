#!/usr/bin/env bash
# One-off restart for SCALD_WATER_AGITATION_FLECKS_1 + RIVER_STEAM_ANIMATION_1
# live-verify. Kills the running campaign (already save-netted via rimworld/save_game
# to rimbridge_save_20260925_130651.rws), deploys the 3 locked DLLs, relaunches via
# Steam (never bare exe), waits for THIS run's bridge marker.
set -u
cd /mnt/d/Luke/dev/Rimworld

LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
MARK="GABP server running standalone"
BEFORE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
START=$(date +%s)

echo "[1/5] killing RimWorldWin64.exe"
taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1
sleep 4

echo "[2/5] deploying the 3 locked DLLs now that the process is dead"
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod EnvironmentalHazards --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaRules --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply

echo "[3/5] launching via Steam"
cmd.exe /c start "" "steam://rungameid/294100" 2>/dev/null

echo "[4/5] waiting for log truncate"
for i in $(seq 1 90); do
  sleep 2
  NOW=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
  [ "$NOW" -lt "$BEFORE" ] && break
  [ "$BEFORE" -eq 0 ] && [ "$NOW" -gt 0 ] && break
done
echo "log truncated after $(( $(date +%s)-START ))s (was $BEFORE, now $(stat -c %s "$LOG" 2>/dev/null))"

echo "[5/5] waiting for THIS run's bridge marker"
for i in $(seq 1 300); do
  grep -q "$MARK" "$LOG" 2>/dev/null && { echo "BRIDGE UP after $(( $(date +%s)-START ))s"; exit 0; }
  tasklist.exe 2>/dev/null | grep -qi rimworld || { echo "PROCESS GONE after $(( $(date +%s)-START ))s"; exit 1; }
  sleep 3
done
echo "TIMEOUT after $(( $(date +%s)-START ))s"; exit 1
