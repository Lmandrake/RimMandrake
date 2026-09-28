#!/bin/bash
# biome_load_proof.sh — BIOME_LOAD_PROOF_WAVE_1
#
# ⛔ RETIRED 2026-09-28 (BAROQUE_BIOMES_WAVE2_FOLD_1). Every biome this script
# targets is now folded into mandrake.rm.biomes; deploy_custom_mods.py
# refuses to deploy a folded mod standalone (points at --compose biomes
# instead) and modset_builder.py's proof_<biome> tiers this script calls are
# deleted. BIOME_LOAD_PROOF_WAVE_1 is dropped — superseded by the unification
# waves' own load-proving, which covers every one of these biomes together
# (see design/RimMandrake/biome_mod_unification_spec.md's "EXECUTED" section).
# Left in place as a record of the method, not something to run again.
#
# Proves each biome mod loads CLEAN, ALONE, on a dependency-complete minimal list.
# That is the owner's deliberately narrow sense of PROVEN (2026-09-26): "PROVEN
# doesn't mean fully functional, it means PROVEN for donor retirement purposes."
# It says nothing about playability, art or mechanics.
#
# Per biome:
#   modset_builder.py --tier proof_<biome> --apply   (resolves <modDependencies>;
#      the loadsweep gen_config.py base list does NOT, which is why this uses
#      modset_builder instead of sweep_load.sh)
#   kill game -> rotate Player.log -> launch via Steam -> poll -> grep -> def check
#
# 🔴 Launch goes through Steam, never the bare .exe: a raw .exe launch
#    intermittently corrupts Harmony assembly resolution (skill §10, measured).
# 🔴 The bridge def check runs under python.exe, never WSL python: RimBridge binds
#    Windows loopback and WSL2 is NAT-mode, so there is no route from here.
#
# Usage:  ./biome_load_proof.sh <biome> [<biome> ...]
#         ./biome_load_proof.sh --all
set -u

REPO="/mnt/d/Luke/dev/Rimworld"
DIR="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
LOG="$LOGDIR/Player.log"
CFG="$LOGDIR/Config/ModsConfig.xml"
OUT="$REPO/Transient/biome_load_proof_results.tsv"
STEAM="/mnt/c/Program Files (x86)/Steam/steam.exe"

ALL_BIOMES="bluedesert contagion feverwood floodedcanyon forsakencrags gelatinousslime greentide leaningscrub longshade miasma nightsideice poisonforest pyrelands rustcathedral stillsand terminalbiomes theforge therot thesump wasteland webwork weepingstones"

if [ "${1:-}" = "--all" ]; then set -- $ALL_BIOMES; fi
if [ $# -eq 0 ]; then echo "usage: $0 <biome>... | --all"; exit 2; fi

# The BiomeDef each mod must prove present. Mods whose biome defName differs from
# the packageId stem, or that carry several biomes, are listed explicitly.
defname_for() {
  case "$1" in
    gelatinousslime) echo "RM_GelatinousSlime" ;;
    floodedcanyon)   echo "RM_FloodedCanyon" ;;
    nightsideice)    echo "RM_NightsideIce" ;;
    poisonforest)    echo "RM_PoisonForest" ;;
    wasteland)       echo "RM_Wasteland" ;;
    leaningscrub)    echo "RM_LeaningScrub" ;;
    terminalbiomes)  echo "RM_TheScald" ;;   # kit mod: 4 biomes, Scald is the probe
    theforge)        echo "RM_TheForge" ;;
    therot)          echo "RM_TheRot" ;;
    thesump)         echo "RM_TheSump" ;;
    weepingstones)   echo "RM_WeepingStones" ;;
    forsakencrags)   echo "RM_ForsakenCrags" ;;
    rustcathedral)   echo "RM_RustCathedral" ;;
    bluedesert)      echo "RM_BlueDesert" ;;
    feverwood)       echo "RM_FeverWood" ;;
    longshade)       echo "RM_LongShade" ;;
    lanterndeeps)    echo "RM_LanternDeeps" ;;
    *)               echo "RM_$(python3 -c "print('$1'.capitalize())")" ;;
  esac
}

if [ ! -f "$OUT" ]; then
  printf 'biome\tverdict\tload_s\tactive_mods\tbiomedef\tdef_present\tdistinct_errors\tcfgerr_lines\txref_lines\tpatchfail_lines\ttypeload_lines\trecovery_lines\tnote\n' > "$OUT"
fi

for BIOME in "$@"; do
  DEFNAME="$(defname_for "$BIOME")"
  echo "════════ $BIOME  (expect $DEFNAME) ════════"

  # 🔴 Kill FIRST, then write the tier. modset_builder refuses to write while
  # Player.log has been touched in the last 3 minutes, so applying before the
  # kill fails every time. (Its refusal message claims the game rewrites
  # ModsConfig on exit — that is false, measured 2026-08-13; the guard is still
  # right, because a running game holds its list in memory and an in-game change
  # would clobber the write.)
  taskkill.exe /F /IM RimWorldWin64.exe >/dev/null 2>&1
  sleep 10
  mv -f "$LOG" "$LOG.prev" 2>/dev/null
  # Player.log is now rotated away, so the liveness heuristic sees no fresh log.

  if ! (cd "$REPO" && python3 src/RimMandrake/Utils/modset_builder.py --tier "proof_$BIOME" --apply >/tmp/mb.$$ 2>&1); then
    echo "  TIER FAILED"; tail -4 /tmp/mb.$$
    printf '%s\tTIER_FAILED\t-\t-\t%s\t-\t-\t-\t-\t-\t-\tmodset_builder refused\n' "$BIOME" "$DEFNAME" >> "$OUT"
    continue
  fi
  NMODS=$(grep -oE '^ *[0-9]+ mods,' /tmp/mb.$$ | grep -oE '[0-9]+' | head -1)
  echo "  tier applied: ${NMODS:-?} mods"

  "$STEAM" -applaunch 294100 >/dev/null 2>&1 &
  disown
  START=$(date +%s)

  VERDICT="TIMEOUT"; ELAPSED="-"
  for i in $(seq 1 100); do
    sleep 3
    [ -f "$LOG" ] || continue
    if grep -q "Bridge token:" "$LOG" 2>/dev/null; then
      VERDICT="UP"; ELAPSED=$(( $(date +%s) - START )); break; fi
    if grep -q "Recovered from incompatible or corrupted mods" "$LOG" 2>/dev/null; then
      VERDICT="RECOVERY_RESET"; ELAPSED=$(( $(date +%s) - START )); break; fi
    if grep -q "Caught exception while loading play data" "$LOG" 2>/dev/null; then
      VERDICT="LOAD_ABORT"; ELAPSED=$(( $(date +%s) - START )); break; fi
  done
  echo "  $VERDICT after ${ELAPSED}s"

  # 🔴 These are OCCURRENCE counts (lines), NOT error counts. One error can span
  # 30 lines of stack trace. `measure count-errors` gives the DISTINCT figure and
  # is the only thing allowed to be called an error count — the repo's
  # block_blind_scan hook refuses a bare grep census of a Player.log and is right
  # to. The verdict below rests on bridge-up + def-present, never on these.
  # ⚠️ `grep -c` prints 0 AND exits 1 on no match, so a `|| echo 0` fallback
  # emits TWO lines and every count came out as "0\n0". Take the first line only.
  count() { MEASURE_ALLOW_SCAN=1 grep -cE "$1" "$LOG" 2>/dev/null | head -1 | tr -dc '0-9'; }
  CE=$(count '^Config error in'); CE=${CE:-0}
  XR=$(count 'Could not resolve cross-reference'); XR=${XR:-0}
  PF=$(count 'Patch operation.*failed'); PF=${PF:-0}
  TL=$(count '(ReflectionTypeLoadException|TypeLoadException)'); TL=${TL:-0}
  RC=$(count 'Recovered from incompatible'); RC=${RC:-0}
  DISTINCT=$(PATH="$HOME/.claude/skills/measuring-large-artifacts/bin:$PATH" \
    measure count-errors "$LOG" 2>/dev/null | grep -oE 'MEASURED [0-9]+' | grep -oE '[0-9]+' | head -1)
  DISTINCT=${DISTINCT:-UNMEASURED}
  AM=$(python3 -c "import xml.etree.ElementTree as ET;print(len(ET.parse(r'$CFG').getroot().find('activeMods')))" 2>/dev/null || echo '-')

  # Positive check: is the BiomeDef actually in the loaded def set? Absence of
  # errors is NOT a pass -- a patch that matches nothing logs nothing.
  PRESENT="UNMEASURED"
  if [ "$VERDICT" = "UP" ]; then
    # ⚠️ python.exe emits CRLF. Without `tr -d '\r'` the value is "PRESENT\r",
    # every string compare below fails, and a clean load records as FAIL.
    PRESENT=$(cd "$REPO" && python.exe src/RimMandrake/Utils/loadsweep/check_biome_present.py "$DEFNAME" 2>/dev/null | tail -1 | tr -d '\r\n')
    [ -z "$PRESENT" ] && PRESENT="UNMEASURED"
  fi
  echo "  biomedef $DEFNAME: $PRESENT   ($DISTINCT distinct errors; lines: cfg $CE, xref $XR, patch $PF, typeload $TL)"

  FINAL="FAIL"
  if [ "$VERDICT" = "UP" ] && [ "$PRESENT" = "PRESENT" ]; then FINAL="PASS"; fi
  if [ "$VERDICT" = "UP" ] && [ "$PRESENT" = "UNMEASURED" ]; then FINAL="UNMEASURED"; fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' \
    "$BIOME" "$FINAL" "$ELAPSED" "${AM:--}" "$DEFNAME" "$PRESENT" "$DISTINCT" "$CE" "$XR" "$PF" "$TL" "$RC" >> "$OUT"
  echo "  => $FINAL"
done

echo
echo "🔴 RESTORE THE OWNER'S LIST before he plays:"
echo "   python3 src/RimMandrake/Utils/modlist_swap.py --restore --apply"
echo "results: $OUT"
