#!/usr/bin/env bash
# shutdown_deploy.sh — the three deploys that need RimWorld DOWN, in order, with guards.
#
# Written by OPS 2026-08-14 at wrap, when the game was STILL UP and the window never
# opened. Everything below was staged and verified that day; nothing was shipped.
#
#   S8  BridgeTools companion   (CHECK's, --gm REQUIRED, rides free)
#   S1  JawaSeaShaper.dll       (mod assembly, SOLO load)
#   S9  Jawa_Patches            (scrapfields minSpacing 4->1, 8a7a5ee — the v1 row 4 fix)
#
# Run from the repo root:  ./src/RimMandrake/Utils/shutdown_deploy.sh
# Add --yes to skip the confirmation prompt.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 1

# --- Guard: the game must be gone. -------------------------------------------
# A write under common\RimWorld\ fails OSError 22 while RimWorld holds the file.
# That refusal is SAFE (it cannot truncate) but a run that skips silently is not.
if tasklist.exe /FI "IMAGENAME eq RimWorldWin64.exe" 2>/dev/null | grep -q RimWorldWin64; then
  echo "REFUSING: RimWorld is still running. This window is not open yet."
  exit 1
fi
echo "Game is down. Proceeding."

if [ "${1:-}" != "--yes" ]; then
  read -r -p "Deploy S8 (BridgeTools --gm), S1 (SeaShaper), S9 (Jawa_Patches)? [y/N] " a
  [ "$a" = "y" ] || { echo "Aborted."; exit 1; }
fi

fail=0

# --- S8 -----------------------------------------------------------------------
# NOTE: build.py --apply REBUILDS before deploying. The artifact verified at wrap was
# md5 d7e7c6c1 / 30 tools, but a rebuild legitimately produces different bytes.
# => Do NOT gate on that md5 afterwards. Gate on the CANARIES, checked below.
echo; echo "=== S8  BridgeTools (--gm) ==="
python3 src/RimMandrake/bridgetools/build.py --gm --apply || { echo "S8 FAILED"; fail=1; }

# --- S1 -----------------------------------------------------------------------
echo; echo "=== S1  JawaSeaShaper.dll (SOLO) ==="
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaSeaShaper --apply || { echo "S1 FAILED"; fail=1; }

# --- S9 -----------------------------------------------------------------------
echo; echo "=== S9  Jawa_Patches — scrapfields minSpacing 1 ==="
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Jawa_Patches --apply || { echo "S9 FAILED"; fail=1; }

# --- Post-verify: the two --gm canaries, read from the DEPLOYED copy ----------
# Missing either means fire_incident/send_letter were stripped — the exact failure
# --gm exists to prevent, and it is silent without this check.
echo; echo "=== verifying the deployed companion ==="
D="/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/BridgeTools/JawaBench/JawaBench.BridgeTools.dll"
if [ -f "$D" ]; then
  n=$(strings -a "$D" | grep -c '^jawa/')
  echo "  deployed tools: $n"
  for t in fire_incident send_letter; do
    if strings -a "$D" | grep -qx "jawa/$t"; then echo "  OK   jawa/$t"
    else echo "  MISSING  jawa/$t  <-- --gm did not take. DO NOT LAUNCH ON THIS."; fail=1; fi
  done
else
  echo "  MISSING: $D"; fail=1
fi

# strings -a proves NAMES only, never a method body (UTF-16LE literals live in #US;
# use strings -a -el for those). Do not read this as behavioural verification.

echo
if [ "$fail" = 0 ]; then
  echo "ALL THREE DEPLOYED. Next load: full-map ChunkSlagSteel count (expect 44-56 in ~5"
  echo "clumps) on a map GENERATED AFTER THIS DEPLOY — name the map — and grep the log"
  echo "for a GenStep_ScatterThings.ScatterAt NRE: gone => it was ours, still there =>"
  echo "it is Biomes Core's. Both ride work already scheduled."
else
  echo "ONE OR MORE STEPS FAILED — read the output above before launching."
  exit 1
fi
