#!/bin/bash
# one chain per driver run, each on a freshly reloaded visit-2 site; progress in Transient/pv2/runner.progress
export RM_ALLOW_CONCURRENT_BRIDGE=1; export WSLENV="${WSLENV:+$WSLENV:}RM_ALLOW_CONCURRENT_BRIDGE:RM_GAME_INSTANCE"   # sequential runs under our own bridge hold; the guard saw the last run's final call
cd /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO.det
E=design/concepts/Pyrelands/version/in_game/visit_2/evidence
P=Transient/pv2/runner.progress
for spec in "$@"; do
  name=${spec//,/+}; name=${name##*/}; name=${name%.py}
  echo "$(date +%T) START $spec" >> $P
  timeout 300 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint bf7f9e1fe4 --tag visit2 --reload-only --tile 3 > Transient/pv2/reload_$name.log 2>&1
  rr=$?
  if [ $rr -ne 0 ]; then echo "$(date +%T) RELOAD_FAIL rc=$rr $spec" >> $P; continue; fi
  case "$spec" in
    script:*) sp=${spec#script:}; name=$(basename "$sp" .py)
              timeout 2400 python.exe "$sp" > $E/script_$name.log 2>&1; rc=$? ;;
    *) timeout 2400 python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains "$spec" --out $E/pv2_$name.json > Transient/pv2/run_$name.log 2>&1
       rc=$? ;;
  esac
  echo "$(date +%T) END rc=$rc $spec" >> $P
done
echo "$(date +%T) ALLDONE" >> $P
