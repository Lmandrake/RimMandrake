#!/usr/bin/env bash
# sitting.sh <game>: the one live sitting of RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME, run inside
# `game_lock.py run <game>` (the lock is held for the life of this script). Three proofs, in the brief's order:
#   1. FlowWorks shrunk scenes on the exact tier the test table names (flowworks, 13 mods; sc_lake_endless on
#      fw_gss_sitting), rows by bundle_shrink_20261125/run_row.py;
#   2. HARNESS_REPAIR_CAUSE_8135787B_3: the job J20261124T065455Z-c5e072's chains, direct modcheck on flowworks_list;
#   4. HARNESS_REPAIR_CAUSE_F6CADE57_2: both Pyrelands sightings' chains, direct modcheck on pyrelands.
# Each load is checked against the tier's exact list before anything runs on it (run 2 of the shrink pass ran on a
# 24-mod list because its check was only "30 mods or fewer"). Each modcheck is run the way the lane worker runs it
# (list kept, deploy done first) and turned into a testq-shaped record by direct_record.py, so `retest.py passed
# <record>` judges it with the same code as a lane job. No time limit here: the parent watches log growth.
g=$1
ONLY=${2:-1,2,4}
cd "$(dirname "$0")/../../../../../.." || exit 2
ROOT=$(pwd)
H=design/concepts/FlowWorks/version/in_game/harness_rerun_20261125
P=design/concepts/Pyrelands/version/in_game/harness_rerun_20261125
B=design/concepts/FlowWorks/version/in_game/bundle_shrink_20261125
U=src/RimMandrake/Utils
CS=src/RimMandrake/FlowWorks/northstar/concept_scenes.py
S=/mnt/d/ClaudeWork/scratch/rerun_two_harness_20261125
mkdir -p $S
L=$S/sitting.log
eval "$(python3 $U/game_instance.py env $g)"
SHA=$(git rev-parse --short=10 HEAD)
echo "GAME=$g sha=$SHA only=$ONLY at $(date +%H:%M:%S)" >> $L
step() { echo "STEP $* at $(date +%H:%M:%S)" >> $L; "$@" >> $L 2>&1; local rc=$?; echo "STEP_RC=$rc" >> $L; return $rc; }
python3 src/RimMandrake/rimflow/cli.py bridge take --host $g --idle-ok --seat BENCH \
  --for "RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME sitting" --why "detached run: live sitting" --publish >> $L 2>&1
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
load() {    # load <tier>: game down, tier written (an owned swap of this run), exact check, game up
  step python3 $U/game_instance.py stop --instance $g --for "rerun sitting: load $1" || return 10
  step python3 $U/modset_builder.py --tier "$1" --apply --by "rerun2h_$1_$(date +%H%M%S)" || return 12
  exact "$1" || { echo "TIER NOT EXACT: $1" >> $L; return 13; }
  step python3 $U/game_instance.py launch $g --wait || return 14
  step python3 $B/wait_bridge.py || return 15
}
modcheck() {   # modcheck <name> <mod> <chains> <job id of the sighting> <record dir>
  local n=$1 mod=$2 ch=$3 jid=$4 dir=$5 log=$S/$1_modcheck.log
  echo "STEP modcheck $mod $ch at $(date +%H:%M:%S)" >> $L
  ( export MODCHECK_KEEP_MODLIST=1 MODCHECK_SKIP_DEPLOY=1
    export WSLENV=${WSLENV:+$WSLENV:}MODCHECK_KEEP_MODLIST:MODCHECK_SKIP_DEPLOY
    python.exe -X faulthandler $U/modcheck/cli.py run --drivers on "$mod" --chains "$ch" --canary --validity \
      --reuse off --purpose fix --gate shadow > $log 2>&1; echo "MODCHECK_RC=$?" >> $log )
  tail -1 $log >> $L
  python3 $H/direct_record.py "$ROOT" $log $dir/${n}_record.json "DIRECT-$n-$(date +%Y%m%dT%H%M%S)" "$mod" "$ch" "$SHA" "$g" >> $L 2>&1
}

if [[ ,$ONLY, == *,1,* ]]; then
  step python3 $U/game_instance.py stop --instance $g --for "rerun sitting: deploy FlowWorks" || exit 10
  step python3 $U/deploy_custom_mods.py --mod FlowWorks --apply --instance $g || exit 11
  git log -1 --format=%H -- src/RimMandrake/FlowWorks > $B/DEPLOYED_SHA
  if load flowworks; then
    for t in sc_walk_reload sc_walk_switch sc_walk_second_order sc_source_draws sc_source_refills sc_sprinkler_pump \
             sc_faucet_drink sc_hole_prison sc_pawn_height; do
      python3 $B/run_row.py $t --tier flowworks --timeout 1800 -- python.exe -u $CS --scene "scene_${t#sc_}" --out OUT 2>&1 | head -3 >> $L
    done
    python3 $B/run_row.py sc_hung_bridge --tier flowworks --site-key site_calm.ok --timeout 1800 -- \
      python.exe -u src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py OUT --only posts,under 2>&1 | head -3 >> $L
  else echo "PROOF1 flowworks tier not loaded" >> $L; fi
  if load fw_gss_sitting; then
    python3 $B/run_row.py sc_lake_endless --tier fw_gss_sitting --timeout 1800 -- \
      python.exe -u $CS --scene scene_lake_endless --out OUT 2>&1 | head -3 >> $L
  else echo "PROOF1 fw_gss_sitting tier not loaded" >> $L; fi
fi
if [[ ,$ONLY, == *,2,* ]]; then
  step python3 $U/game_instance.py stop --instance $g --for "rerun sitting: deploy FlowWorks"
  step python3 $U/deploy_custom_mods.py --mod FlowWorks --apply --instance $g
  if load flowworks_list; then
    modcheck 8135787B FlowWorks thirst,hose_live_rows,canal_overflow,sprinklers J20261124T065455Z-c5e072 $H
  else echo "PROOF2 flowworks_list not loaded" >> $L; fi
fi
if [[ ,$ONLY, == *,4,* ]]; then
  step python3 $U/game_instance.py stop --instance $g --for "rerun sitting: deploy Pyrelands"
  step python3 $U/deploy_custom_mods.py --instance $g --compose biomes --apply
  if load pyrelands; then
    modcheck F6CADE57_a Pyrelands full_list_smoke,reload_keeps_the_burn,scorchfruit_spoils,opening_front J20261124T102230Z-9fc065 $P
    modcheck F6CADE57_b Pyrelands ash_fertility_watered,burrowers,fresh_burn_bonus,burn_line J20261124T160452Z-a771c4 $P
  else echo "PROOF4 pyrelands not loaded" >> $L; fi
fi
echo "SITTING DONE at $(date +%H:%M:%S)" >> $L
