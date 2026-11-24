#!/bin/bash
# Pyrelands visit 8: the two-week walk on his full list (ArchBig): reload the full-list site fixture, then walk_season with
# PYRE_WALK=1. usage: walk_full.sh <label> [VAR=VAL ...]   (extra VAR=VAL: a planted fault, passed through WSLENV)
cd "$(dirname "$0")/../../../../../../.."
E=design/concepts/Pyrelands/version/in_game/visit_8/evidence
LAB=$1; shift
export RM_GAME_INSTANCE=a RM_HOST_GUARD_GEN=43 RM_BRIDGE_LINEAGE=pv8_visit8 PYRE_WALK=1
export WSLENV="$WSLENV:RM_GAME_INSTANCE:RM_HOST_GUARD_GEN:RM_BRIDGE_LINEAGE:PYRE_WALK:PYRE_PLANT_GATE_IGNORED:PYRE_WALK_PARTS_ONLY:PYRE_WALK_ONE"
for kv in "$@"; do export "$kv"; done
t0=$(date +%s)
python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5e402 --tag visit8full2 \
    --reload-only --tile 23589 --map-id 1 --out Transient/pv8_site_1_full_reload.json 2>&1 | tr -d '\r' \
    | grep -v "safe.directory\|dubious\|non-local\|add an exception" > $E/reload_$LAB.log
rl=${PIPESTATUS[0]}
python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py \
    --no-record --chains walk_season --out $E/pv8_$LAB.json 2>&1 | tr -d '\r' \
    | grep -v "safe.directory\|dubious\|non-local\|add an exception" > $E/run_$LAB.log
rc=${PIPESTATUS[0]}
echo "DONE ${*:+$* }walk_season@$LAB (full list) reload_rc=$rl rc=$rc $(( $(date +%s) - t0 ))s $(date '+%T')" >> $E/runner.log
