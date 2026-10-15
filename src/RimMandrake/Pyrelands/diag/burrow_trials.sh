#!/bin/bash
# Burrow diagnostic trials (TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL, TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED).
# One COLD trial per site-fixture reload: a second fire on the same map is warm (standing-burn window), and repeats on one
# map cooked the support colonists. Runs the validation.py chain `burrowers_diag`, which exists only with PYRE_BURROW_DIAG=1.
# Needs: bridge held, game up on the pyrelands tier, the site fixture built by northstar_site.py.
#   src/RimMandrake/Pyrelands/diag/burrow_trials.sh FIRST LAST [FINGERPRINT] [TAG] [TILE]
# Defaults reproduce the 2026-10-14 BENCH run (26 cold trials, 0 colonist harm).
# Runs from the read-only mirror (python.exe cannot read the WSL seat clone): push first, then `./mirror sync`.
set -u
MIRROR=/mnt/d/Luke/dev/RimMandrake
FP=${3:-417df172fdb5}; TAG=${4:-r2}; TILE=${5:-3}
OUTW='D:\Luke\dev\_rmscratch\burrow_trials'           # program-read output: outside the repo
mkdir -p /mnt/d/Luke/dev/_rmscratch/burrow_trials
cd "$MIRROR" || exit 2
export PYRE_BURROW_DIAG=1 BURROW_QUIET=${BURROW_QUIET:-10} BURROW_NEAR=1 BURROW_CTRL=0 BURROW_SAMPLES=${BURROW_SAMPLES:-40}
export WSLENV=PYRE_BURROW_DIAG:BURROW_NEAR:BURROW_CTRL:BURROW_DIAG_OUT:BURROW_QUIET:BURROW_SAMPLES
for n in $(seq "${1:-1}" "${2:-10}"); do
  echo "== trial $n $(date +%T)"
  timeout 240 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint "$FP" --tag "$TAG" \
      --reload-only --tile "$TILE" --work "$OUTW\\sites" 2>&1 | tail -1 | cut -c1-200
  export BURROW_DIAG_OUT="$OUTW\\burrow_cold_$n.json"
  timeout 400 python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands \
      --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains burrowers_diag --no-record \
      --out "$OUTW\\burrow_run_$n.json" 2>&1 | grep -E "\[diag\]|PASS|FAIL|ERROR|stopped|Traceback|refus" | cut -c1-400 | tail -6
done
echo "== done $(date +%T)"
