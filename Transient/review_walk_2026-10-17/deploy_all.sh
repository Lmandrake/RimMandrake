#!/usr/bin/env bash
# Apply every owed deploy for the 2026-10-17 review walk. GAME MUST BE DOWN (deploy_custom_mods.py checks ./game and refuses).
# Deploys, then writes the walk's ModsConfig.xml (walk_modlist.py, backed up first; modset.md). Game down only.
# Plans: Transient/review_walk_2026-10-17/deploy_plan_*.txt. Run from /home/mandrake/rm/bench.
set -u
cd /home/mandrake/rm/bench || exit 2
D=src/RimMandrake/Utils/deploy_custom_mods.py
LOG=Transient/review_walk_2026-10-17/deploy_all.log
: > "$LOG"
rc=0
run() { echo "=== $*" | tee -a "$LOG"; python3 $D "$@" >> "$LOG" 2>&1 || { echo "FAILED: $*" | tee -a "$LOG"; rc=1; }; tail -2 "$LOG"; }
# order as asked. LeaningScrub, EnvironmentalHazards and ExplosiveGrowth are folded into the composed mod: they ship ONLY via --compose biomes.
run --apply --mod FlowWorks
run --apply --compose biomes
run --apply --mod UtinniPatches
run --apply --mod SWBestiary
run --apply --mod StarWarsPatches
run --apply --mod Doctrine
run --apply --mod Armoury
run --apply --mod PawnFlavor
# Mod list for the walk (backs up the live ModsConfig.xml first; see modset.md). Refused while the game is up.
if ./game 2>&1 | grep -q 'RUNNING'; then echo "game is RUNNING: ModsConfig NOT written" | tee -a "$LOG"; rc=1
else python3 Transient/review_walk_2026-10-17/walk_modlist.py --apply 2>&1 | tail -4 | tee -a "$LOG" || rc=1; fi
echo "deploy_all done rc=$rc (log: $LOG)"
exit $rc
