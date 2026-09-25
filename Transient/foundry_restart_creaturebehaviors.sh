#!/usr/bin/env bash
# Second restart this session: deploy the stale RimMandrake.CreatureBehaviors.dll
# (CREATUREBEHAVIORS_DLL_DEPLOY_DRIFT_1) that was crashing GeneticRim.Core's static
# ctor and breaking all pawn generation. Campaign was save-netted to
# rimbridge_save_20260925_134920.rws (scratch-test state) first; the real campaign
# continuity point is rimbridge_save_20260925_130651.rws, loaded after this restart.
set -u
cd /mnt/d/Luke/dev/Rimworld

LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
MARK="GABP server running standalone"
BEFORE=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
START=$(date +%s)

echo "[1/5] killing RimWorldWin64.exe"
taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1
sleep 4

echo "[2/5] deploying CreatureBehaviors DLL now that the process is dead"
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod CreatureBehaviors --apply

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
