#!/bin/bash
# One sweep cycle: write config, restart game via Steam, poll to ready, grep verdicts.
set -u
BATCH="$1"
DIR="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
LOG="$LOGDIR/Player.log"
CFG="$LOGDIR/Config/ModsConfig.xml"

python3 "$DIR/gen_config.py" "$BATCH" || exit 2

taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1
sleep 8
mv -f "$LOG" "$LOG.prev" 2>/dev/null

"/mnt/c/Program Files (x86)/Steam/steam.exe" -applaunch 294100 &
disown

echo "launched $(date +%T); polling for bridge ready (max 420s)"
for i in $(seq 1 140); do
  sleep 3
  if [ -f "$LOG" ]; then
    if grep -q "Bridge token:" "$LOG" 2>/dev/null; then echo "BRIDGE UP after ~$((i*3))s"; break; fi
    if grep -q "Recovered from incompatible or corrupted mods" "$LOG" 2>/dev/null; then echo "RECOVERY-RESET after ~$((i*3))s"; break; fi
  fi
done

echo "=== verdict lines ==="
grep -E "\[JawaBench\] (ready|context)" "$LOG" 2>/dev/null
echo "recovery_hits: $(grep -c 'Recovered from incompatible' "$LOG" 2>/dev/null)"
echo "config_errors: $(grep -c '^Config error in' "$LOG" 2>/dev/null)"
echo "crossref_errors: $(grep -c 'Could not resolve cross-reference' "$LOG" 2>/dev/null)"
echo "patch_failed: $(grep -cE 'Patch operation.*failed' "$LOG" 2>/dev/null)"
echo "typeload: $(grep -cE '(ReflectionTypeLoadException|TypeLoadException)' "$LOG" 2>/dev/null)"
echo "disk_active_mods: $(python3 -c "import xml.etree.ElementTree as ET;print(len(ET.parse('$CFG').getroot().find('activeMods')))" 2>/dev/null)"
echo "=== done ==="
