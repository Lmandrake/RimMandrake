#!/usr/bin/env bash
# take.sh <name> <mod> <chains,csv>: take the first free Archmagi game (ArchBig, then ArchSmall; 75 = held, try the
# next) and run rerun.sh on it under `game_lock.py run`. No bound on the wait: a held game is another live run, not a
# hang; the caller (waitalive.py) watches the log for life.
cd "$(dirname "$0")/../../.." || exit 2
HERE=design/specs/2026-11-26-test-lane-bundle-reruns
while true; do
  for g in ArchBig ArchSmall; do
    python3 src/RimMandrake/rimflow/game_lock.py query $g >/dev/null 2>&1 || continue
    echo "TRY $g for $1 at $(date +%H:%M:%S)"
    python3 src/RimMandrake/rimflow/game_lock.py run $g --for "WB-pipeline-test-lane-20261126-024244: re-run $1 ($2 $3)" \
      -- bash $HERE/rerun.sh $g "$1" "$2" "$3"
    rc=$?
    if [ $rc != 75 ]; then echo "RAN $1 on $g rc=$rc at $(date +%H:%M:%S)"; exit $rc; fi
  done
  sleep 20
done
