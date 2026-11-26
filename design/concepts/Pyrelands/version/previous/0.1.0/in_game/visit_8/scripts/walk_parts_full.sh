#!/bin/bash
# Pyrelands visit 8: the later parts of sc_walk on his full list, on the save its second week ended on (pyre_walk_end: the same site,
# the same build), PYRE_WALK_PARTS_ONLY=1. usage: walk_parts_full.sh <label>
cd "$(dirname "$0")/../../../../../../.."
E=design/concepts/Pyrelands/version/in_game/visit_8/evidence
LAB=$1; shift
export RM_GAME_INSTANCE=a RM_HOST_GUARD_GEN=43 RM_BRIDGE_LINEAGE=pv8_visit8 PYRE_WALK=1 PYRE_WALK_PARTS_ONLY=1 AGENT_SEAT=BENCH
for kv in "$@"; do export "$kv"; done
export WSLENV="$WSLENV:RM_GAME_INSTANCE:RM_HOST_GUARD_GEN:RM_BRIDGE_LINEAGE:PYRE_WALK:PYRE_PLANT_GATE_IGNORED:PYRE_WALK_PARTS_ONLY:PYRE_WALK_ONE:AGENT_SEAT:PEEK_SAVE:PEEK_TILE"
t0=$(date +%s)
PEEK_SAVE=pyre_walk_end PEEK_TILE=23589 python.exe design/concepts/Pyrelands/version/in_game/visit_8/scripts/need_peek.py 2>&1 | tr -d '\r' > $E/reload_$LAB.log
rl=${PIPESTATUS[0]}
[[ $rl == 0 ]] || { echo "STOPPED at $LAB: reload_rc=$rl" >> $E/runner.log; exit 3; }
python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py \
    --no-record --chains walk_season --out $E/pv8_$LAB.json 2>&1 | tr -d '\r' \
    | grep -v "safe.directory\|dubious\|non-local\|add an exception" > $E/run_$LAB.log
rc=${PIPESTATUS[0]}
echo "DONE ${*:+$* }walk_season@$LAB (full list, later parts) reload_rc=$rl rc=$rc $(( $(date +%s) - t0 ))s $(date '+%T')" >> $E/runner.log
