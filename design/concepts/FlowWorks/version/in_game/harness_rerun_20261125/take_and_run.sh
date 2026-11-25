#!/usr/bin/env bash
# take_and_run.sh [proofs]: take the first free Archmagi game (ArchBig, then ArchSmall; 75 = held, try again) and run
# sitting.sh on it under `game_lock.py run`. No bound on the wait: a held game is another live run, not a hang.
cd "$(dirname "$0")/../../../../../.." || exit 2
H=design/concepts/FlowWorks/version/in_game/harness_rerun_20261125
S=/mnt/d/ClaudeWork/scratch/rerun_two_harness_20261125; mkdir -p $S
FOR="RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME: FlowWorks shrunk scenes + HARNESS_REPAIR_CAUSE_8135787B_3 + HARNESS_REPAIR_CAUSE_F6CADE57_2 re-runs"
while true; do
  for g in ArchBig ArchSmall; do
    python3 src/RimMandrake/rimflow/game_lock.py query $g >/dev/null 2>&1 || continue
    echo "TRY $g at $(date +%H:%M:%S)" | tee -a $S/take.log
    python3 src/RimMandrake/rimflow/game_lock.py run $g --for "$FOR" -- bash $H/sitting.sh $g "${1:-1,2,4}"
    rc=$?
    if [ $rc != 75 ]; then echo "RAN $g rc=$rc at $(date +%H:%M:%S)" | tee -a $S/take.log; exit $rc; fi
  done
  sleep 20
done
