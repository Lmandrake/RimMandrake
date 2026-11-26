#!/usr/bin/env bash
# rerun.sh <game> <name> <mod> <chains,csv> <tier>: one harness-repair re-run of work bundle WB-pipeline-test-lane-20261126-024244,
# run inside `game_lock.py run <game>` (take.sh holds the lock). It runs the job the way the SteveDesktop lane worker
# runs it (infrastructure/stevedesktop/worker.py): deploy the mod and the mods of ours its composed list names
# (deploy_closure, deploy_flags), then `modcheck run --drivers on <mod> --chains ... --canary --validity --reuse off`.
# The list is the mod's tier, checked exact before the load, and modcheck keeps it (MODCHECK_KEEP_MODLIST=1): modcheck's
# own compose starts from ModsConfig.MINIMAL.xml, which names kutte.stairs, and no folder on Archmagi holds that mod, so
# a composed run here refuses mod_not_installed (first try, 2026-11-25 8:22 PM PST and 9:15 PM PST on ArchSmall).
# direct_record.py (the precedent's, RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME) turns the run into a
# testq-shaped record, so `retest.py passed <record> <item>` judges it with the lane's own code.
# Why direct: SteveDesktop takes pipeline work only (host_work_switch.py) and the Archmagi testq lane admits no targeted
# job. The permanent fix is RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS.
# Env: RERUN_PRE, a command run on the loaded game before modcheck (e.g. a site the chain's own driver cannot build);
# RERUN_DRIVERS, modcheck's --drivers (default on; off when RERUN_PRE built the site the driver would rebuild).
g=$1; n=$2; mod=$3; ch=$4; tier=$5
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
echo "RERUN $n game=$g mod=$mod chains=$ch tier=$tier sha=$SHA at $(date +%H:%M:%S)" >> "$L"
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
step python3 $U/modset_builder.py --tier "$tier" --apply --by "wbtl_${n}_$(date +%H%M%S)" || exit 12
python3 - "$tier" >> "$L" 2>&1 <<'PY2' || { echo "TIER NOT EXACT: $tier" >> "$L"; exit 13; }
import re, subprocess, sys, xml.etree.ElementTree as ET
sys.path.insert(0, "src/RimMandrake/Utils")
from game_paths import MODS_CONFIG
plan = subprocess.run([sys.executable, "src/RimMandrake/Utils/modset_builder.py", "--tier", sys.argv[1]],
                      capture_output=True, text=True).stdout
want = [m.group(1).lower() for m in re.finditer(r"^\s+\d+\s+(\S+\.\S+)\s{2,}", plan, re.M)]
have = [li.text.lower() for li in ET.parse(MODS_CONFIG).find("activeMods")]
print("EXACT tier %s at %s: want %d, have %d, missing %s, extra %s" % (sys.argv[1], MODS_CONFIG, len(want), len(have),
      sorted(set(want) - set(have)), sorted(set(have) - set(want))))
sys.exit(0 if want and set(want) == set(have) else 1)
PY2
step python3 $U/game_instance.py launch "$g" --wait || exit 14
# python.exe over WSL interop can die at start (UtilAcceptVsock accept4 failed 110, 9:19 PM PST): one more try
step python.exe -u design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125/wait_bridge.py || \
  step python.exe -u design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125/wait_bridge.py || exit 15
if [ -n "$RERUN_PRE" ]; then step bash -c "$RERUN_PRE" || exit 16; fi
log=$S/${n}_modcheck.log
echo "STEP modcheck $mod $ch at $(date +%H:%M:%S)" >> "$L"
( export MODCHECK_SKIP_DEPLOY=1 MODCHECK_KEEP_MODLIST=1
  export WSLENV=${WSLENV:+$WSLENV:}MODCHECK_SKIP_DEPLOY:MODCHECK_KEEP_MODLIST
  python.exe -X faulthandler $U/modcheck/cli.py run --drivers "${RERUN_DRIVERS:-on}" "$mod" --chains "$ch" --canary --validity \
    --reuse off --purpose fix --gate shadow > "$log" 2>&1; echo "MODCHECK_RC=$?" >> "$log" )
tail -2 "$log" >> "$L"
cp "$log" "$HERE/${n}_modcheck.log"
python3 design/concepts/FlowWorks/version/in_game/harness_rerun_20261125/direct_record.py "$ROOT" "$log" \
  "$HERE/${n}_record.json" "DIRECT-$n-$(date +%Y%m%dT%H%M%S)" "$mod" "$ch" "$SHA" "$g" >> "$L" 2>&1
echo "RERUN $n DONE at $(date +%H:%M:%S)" >> "$L"
