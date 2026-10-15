#!/bin/bash
# usage: pyre_piece.sh <name> <chains> [timeout_s]
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261014_r4
export RM_ALLOW_CONCURRENT_BRIDGE=1 WSLENV=RM_ALLOW_CONCURRENT_BRIDGE
timeout 240 python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag r5 --reload-only --tile 3 --work "D:\\Luke\\dev\\_rmscratch\\bench_live_20261014_r4\\sites" 2>&1 | tr -d "\r" | tail -1 | cut -c1-160
timeout ${3:-900} python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains "$2" --no-record --out "D:\\Luke\\dev\\_rmscratch\\bench_live_20261014_r4\\r4\\pyre_$1.json" 2>&1 | tr -d '\r' | grep -v "skipped#" > r4/pyre_$1.log
echo "rc=${PIPESTATUS[0]}"; grep -E "^\[pyre\] .* (PASS|FAIL|UNMEASURED|INFERRED)|NOT GREEN|GREEN|REFUSED|Traceback" r4/pyre_$1.log | cut -c1-300
