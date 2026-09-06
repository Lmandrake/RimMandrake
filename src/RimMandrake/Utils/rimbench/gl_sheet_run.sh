#!/usr/bin/env bash
# gl_sheet_run.sh — MAPGEN_GL_SHEET_1 driver: for each emitted landform recipe,
# place it as the ONLY custom landform, restart RimWorld on the minimal+GL list,
# quicktest, prove it from Player.log ("Landforms: <Id>"), screenshot, remove it.
# One bridge driver; the caller holds the bridge and has stamped the game state.
# Usage: gl_sheet_run.sh <recipes_dir> <out_dir> <modsconfig_minimal_gl.xml> <log>
set -uo pipefail
REC="$1"; OUT="$2"; MC_GL="$3"; RUNLOG="$4"
REPO=/mnt/d/Luke/dev/Rimworld
LL="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
LOG="$LL/Player.log"; CFG="$LL/Config/ModsConfig.xml"; CL="$LL/Config/CustomLandforms-v1"
SS="$LL/Screenshots"
CLIENT="python.exe $REPO/src/RimMandrake/Utils/rimbridge_client.py"
mkdir -p "$OUT"; : > "$RUNLOG"
say(){ echo "$(date +%H:%M:%S) $*" | tee -a "$RUNLOG"; }

cp -f "$MC_GL" "$CFG"; say "ModsConfig <- minimal+GL ($(grep -o '<li>' "$CFG" | wc -l) li)"
for rec in "$REC"/RUT_Gen_*.xml; do
  id=$(basename "$rec" .xml)
  rm -f "$CL"/*.xml; cp -f "$rec" "$CL/$id.xml"; say "[$id] placed as the only custom landform"
  taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1; sleep 8; mv -f "$LOG" "$LOG.prev_glsheet" 2>/dev/null
  "/mnt/c/Program Files (x86)/Steam/steam.exe" -applaunch 294100 & disown
  up=0; for i in $(seq 1 100); do sleep 3; [ -f "$LOG" ] && grep -q "Bridge token:" "$LOG" 2>/dev/null && { up=1; break; }; done
  if [ $up = 0 ]; then say "[$id] BRIDGE NOT UP after 300s — skipping"; continue; fi
  say "[$id] bridge up ~$((i*3))s; $(grep -o 'Loaded .* landforms of which .* custom' "$LOG" | head -1)"
  sleep 5
  $CLIENT --call rimworld/start_debug_game_ready --json {} --yes-i-know-this-is-live --timeout 35 >/dev/null 2>&1
  ready=0; for i in $(seq 1 20); do sleep 5; $CLIENT --call jawa/map_info --json {} --yes-i-know-this-is-live --timeout 20 2>&1 | grep -q '"tile"' && { ready=1; break; }; done
  if [ $ready = 0 ]; then say "[$id] map never became ready — skipping"; continue; fi
  ctx=$(grep -o "Map generator context: TileId: [0-9]*, Landforms: [A-Za-z_,\ ]*" "$LOG" | tail -1)
  say "[$id] $ctx"
  echo "$ctx" | grep -q "Landforms: $id" && say "[$id] PROOF OK" || say "[$id] PROOF FAILED — landform not applied"
  sleep 4
  $CLIENT --call jawa/screenshot_mode --json '{"enabled":true}' --yes-i-know-this-is-live --timeout 20 >/dev/null 2>&1
  sleep 1
  $CLIENT --call jawa/take_screenshot --json "{\"fileName\":\"glsheet_$id\"}" --yes-i-know-this-is-live --timeout 30 >/dev/null 2>&1
  sleep 4
  $CLIENT --call jawa/screenshot_mode --json '{"enabled":false}' --yes-i-know-this-is-live --timeout 20 >/dev/null 2>&1
  [ -f "$SS/glsheet_$id.png" ] && { cp -f "$SS/glsheet_$id.png" "$OUT/$id.png"; say "[$id] screenshot -> $OUT/$id.png"; } || say "[$id] screenshot MISSING"
  echo "$ctx" > "$OUT/$id.log.txt"
done
rm -f "$CL"/*.xml; say "custom landforms removed from live config ($(ls "$CL" | wc -l) left)"
say "DONE"
