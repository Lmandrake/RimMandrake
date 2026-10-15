#!/bin/bash
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261014
export RM_ALLOW_CONCURRENT_BRIDGE=1 BURROW_QUIET=10 BURROW_NEAR=1 BURROW_CTRL=0 BURROW_SAMPLES=40
export WSLENV=RM_ALLOW_CONCURRENT_BRIDGE:BURROW_NEAR:BURROW_CTRL:BURROW_DIAG_OUT:BURROW_QUIET:BURROW_SAMPLES
for n in $(seq ${1:-1} ${2:-10}); do
  echo "== trial $n $(date +%T)"
  timeout 240 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag r2 --reload-only --tile 3 --work 'D:\Luke\dev\_rmscratch\bench_live_20261014\sites' 2>&1 | tail -1 | cut -c1-200
  export BURROW_DIAG_OUT="D:\\Luke\\dev\\_rmscratch\\bench_live_20261014\\burrow_cold_$n.json"
  timeout 400 python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains burrowers_diag --no-record --out "D:\\Luke\\dev\\_rmscratch\\bench_live_20261014\\burrow_run_$n.json" 2>&1 | grep -E "\[diag\]|PASS|FAIL|ERROR|stopped|Traceback|refus" | cut -c1-400 | tail -6
done
echo "== done $(date +%T)"
