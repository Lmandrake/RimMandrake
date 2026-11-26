#!/usr/bin/env bash
# rerun.sh <game> <name> <mod> <chains,csv>: one harness-repair re-run of work bundle WB-pipeline-test-lane-20261126-024244,
# run inside `game_lock.py run <game>` (take.sh holds the lock). It runs the job the way the SteveDesktop lane worker
# runs it (infrastructure/stevedesktop/worker.py): deploy the mod and the mods of ours its composed list names
# (deploy_closure, deploy_flags), `modcheck compose`, start the game on that list, then `modcheck run --drivers on
# <mod> --chains ... --canary --validity --reuse off` with MODCHECK_SKIP_DEPLOY=1 MODCHECK_STALE_KEEP_COMPOSED=1.
# direct_record.py (the precedent's, RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME) turns the run into a
# testq-shaped record, so `retest.py passed <record> <item>` judges it with the lane's own code.
# Why direct: SteveDesktop takes pipeline work only (host_work_switch.py) and the Archmagi testq lane admits no targeted
# job. The permanent fix is RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS.
g=$1; n=$2; mod=$3; ch=$4
cd "$(dirname "$0")/../../.." || exit 2
ROOT=$(pwd)
HERE=design/specs/2026-11-26-test-lane-bundle-reruns
U=src/RimMandrake/Utils
S=$(python3 ~/dev/Lodestar/bin/lib/agent_storage.py)/scratch/test_lane_bundle_reruns_20261126
mkdir -p "$S"
L=$S/sitting.log
eval "$(python3 $U/game_instance.py env "$g")"
SHA=$(git rev-parse --short=10 HEAD)
step() { echo "STEP $* at $(date +%H:%M:%S)" >> "$L"; "$@" >> "$L" 2>&1; local rc=$?; echo "STEP_RC=$rc" >> "$L"; return $rc; }
echo "RERUN $n game=$g mod=$mod chains=$ch sha=$SHA at $(date +%H:%M:%S)" >> "$L"
python3 src/RimMandrake/rimflow/cli.py bridge take --host "$g" --idle-ok --seat BENCH \
  --for "WB-pipeline-test-lane-20261126-024244 re-run $n" --why "work bundle live pass" --publish >> "$L" 2>&1
trap 'python3 src/RimMandrake/rimflow/cli.py bridge release --host "$g" --mine --seat BENCH --why "re-run $n done" --publish >> "$L" 2>&1' EXIT
DEPLOY=$(python3 - "$mod" <<'PY'
import os, sys
sys.path.insert(0, "src/RimMandrake/Utils/testq"); sys.path.insert(0, "infrastructure/stevedesktop")
import schema as S
from worker import deploy_closure
mod = sys.argv[1]
mods = [mod] + [m for m in deploy_closure(mod, os.getcwd()) if m != mod]
print(" ".join("%s %s" % fv for fv in S.deploy_flags(mods, "src")))
PY
) || { echo "DEPLOY CLOSURE FAILED" >> "$L"; exit 11; }
step python3 $U/game_instance.py stop --instance "$g" --for "re-run $n: deploy" || exit 10
step python3 $U/deploy_custom_mods.py $DEPLOY --apply --instance "$g" || exit 11
( export MODCHECK_SKIP_DEPLOY=1 MODCHECK_STALE_KEEP_COMPOSED=1
  export WSLENV=${WSLENV:+$WSLENV:}MODCHECK_SKIP_DEPLOY:MODCHECK_STALE_KEEP_COMPOSED
  step python.exe $U/modcheck/cli.py compose "$mod" ) || exit 12
step python3 $U/game_instance.py launch "$g" --wait || exit 14
step python.exe -u design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125/wait_bridge.py || exit 15
log=$S/${n}_modcheck.log
echo "STEP modcheck $mod $ch at $(date +%H:%M:%S)" >> "$L"
( export MODCHECK_SKIP_DEPLOY=1 MODCHECK_STALE_KEEP_COMPOSED=1
  export WSLENV=${WSLENV:+$WSLENV:}MODCHECK_SKIP_DEPLOY:MODCHECK_STALE_KEEP_COMPOSED
  python.exe -X faulthandler $U/modcheck/cli.py run --drivers on "$mod" --chains "$ch" --canary --validity \
    --reuse off --purpose fix --gate shadow > "$log" 2>&1; echo "MODCHECK_RC=$?" >> "$log" )
tail -2 "$log" >> "$L"
cp "$log" "$HERE/${n}_modcheck.log"
python3 design/concepts/FlowWorks/version/in_game/harness_rerun_20261125/direct_record.py "$ROOT" "$log" \
  "$HERE/${n}_record.json" "DIRECT-$n-$(date +%Y%m%dT%H%M%S)" "$mod" "$ch" "$SHA" "$g" >> "$L" 2>&1
echo "RERUN $n DONE at $(date +%H:%M:%S)" >> "$L"
