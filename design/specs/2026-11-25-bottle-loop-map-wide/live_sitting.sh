#!/usr/bin/env bash
# live_sitting.sh <game>: the live pass of RIMMANDRAKE_TRACE_FLOWWORKS_BOTTLE_LOOP_EMPTY_GONE_NONE_FILLED, run inside
# `game_lock.py run <game>` (the lock is held for the life of this script). The recipe of
# design/concepts/FlowWorks/version/in_game/harness_rerun_20261125/sitting.sh proof 2: game down, FlowWorks deployed,
# tier flowworks_list written and checked exact, game up, modcheck run the way the lane worker runs it (list kept,
# deploy done first) on the one chain toggle_bottle_loop. Its modcheck JSON is copied here as live_<stamp>.json for
# accept_live.py. No time limit here: the parent watches the log's growth.
g=$1
cd "$(dirname "$0")/../../.." || exit 2
U=src/RimMandrake/Utils
B=design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125
HERE=design/specs/2026-11-25-bottle-loop-map-wide
S=/mnt/d/ClaudeWork/scratch/bottle_loop_live_20261125
mkdir -p $S
L=$S/sitting.log
eval "$(python3 $U/game_instance.py env $g)"
echo "GAME=$g sha=$(git rev-parse --short=10 HEAD) at $(date +%H:%M:%S)" >> $L
step() { echo "STEP $* at $(date +%H:%M:%S)" >> $L; "$@" >> $L 2>&1; local rc=$?; echo "STEP_RC=$rc" >> $L; return $rc; }
python3 src/RimMandrake/rimflow/cli.py bridge take --host $g --idle-ok --seat BENCH \
  --for "RIMMANDRAKE_TRACE_FLOWWORKS_BOTTLE_LOOP_EMPTY_GONE_NONE_FILLED live pass" --why "detached run: live sitting" --publish >> $L 2>&1
trap 'python3 src/RimMandrake/rimflow/cli.py bridge release --host $g --mine --seat BENCH --why "sitting done" --publish >> $L 2>&1' EXIT

exact() {   # exact <tier>: the live ModsConfig holds exactly the tier's planned list, else refuse
  python3 - "$1" >> $L 2>&1 <<'PY'
import re, subprocess, sys, xml.etree.ElementTree as ET
sys.path.insert(0, "src/RimMandrake/Utils")
from game_paths import MODS_CONFIG
plan = subprocess.run([sys.executable, "src/RimMandrake/Utils/modset_builder.py", "--tier", sys.argv[1]],
                      capture_output=True, text=True).stdout
want = [m.group(1).lower() for m in re.finditer(r"^\s+\d+\s+(\S+\.\S+)\s{2,}", plan, re.M)]
have = [li.text.lower() for li in ET.parse(MODS_CONFIG).find("activeMods")]
print("EXACT tier %s: want %d, have %d, missing %s, extra %s" % (sys.argv[1], len(want), len(have),
      sorted(set(want) - set(have)), sorted(set(have) - set(want))))
sys.exit(0 if want and set(want) == set(have) else 1)
PY
}

step python3 $U/game_instance.py stop --instance $g --for "bottle loop live pass: deploy FlowWorks" || exit 10
step python3 $U/deploy_custom_mods.py --mod FlowWorks --apply --instance $g || exit 11
step python3 $U/modset_builder.py --tier flowworks_list --apply --by "bottleloop_$(date +%H%M%S)" || exit 12
exact flowworks_list || { echo "TIER NOT EXACT: flowworks_list" >> $L; exit 13; }
step python3 $U/game_instance.py launch $g --wait || exit 14
step python.exe -u $B/wait_bridge.py || exit 15
log=$S/modcheck.log
echo "STEP modcheck FlowWorks toggle_bottle_loop at $(date +%H:%M:%S)" >> $L
mark=$S/modcheck.start; touch $mark
( export MODCHECK_KEEP_MODLIST=1 MODCHECK_SKIP_DEPLOY=1
  export WSLENV=${WSLENV:+$WSLENV:}MODCHECK_KEEP_MODLIST:MODCHECK_SKIP_DEPLOY
  python.exe -X faulthandler $U/modcheck/cli.py run FlowWorks --item FlowWorks=RIMMANDRAKE_TRACE_FLOWWORKS_BOTTLE_LOOP_EMPTY_GONE_NONE_FILLED \
    --chains toggle_bottle_loop --reuse off --purpose fix --gate off > $log 2>&1; echo "MODCHECK_RC=$?" >> $log )
tail -3 $log >> $L
j=$(ls -t Transient/modcheck/FlowWorks_*.json 2>/dev/null | head -1)
if [ -n "$j" ] && [ "$j" -nt $mark ]; then cp "$j" $HERE/live_$(basename "$j" .json | sed 's/^FlowWorks_//').json; echo "COPIED $j" >> $L
else echo "NO NEW modcheck JSON (newest: ${j:-none})" >> $L; fi
echo "SITTING DONE at $(date +%H:%M:%S)" >> $L
