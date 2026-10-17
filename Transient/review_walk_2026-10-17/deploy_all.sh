#!/usr/bin/env bash
# Apply every owed deploy for the 2026-10-17 review walk. GAME MUST BE DOWN (deploy_custom_mods.py checks ./game and refuses).
# Writes files only; it does NOT touch ModsConfig.xml (see STAGING.md section 0 for the mod list the walk needs).
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
echo "deploy_all done rc=$rc (log: $LOG)"
exit $rc
