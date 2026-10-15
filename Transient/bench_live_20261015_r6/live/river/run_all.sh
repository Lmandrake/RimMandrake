#!/bin/bash
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261015_r6
timeout 500 python.exe src/RimMandrake/FlowWorks/northstar/river_site.py 2>&1 | tr -d '\r' > Transient/live/river/river_site_2.log
timeout 1500 python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --out "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_r6\\Transient\\live\\river\\ext_river.json" 2>&1 | tr -d '\r' > Transient/live/river/ext_river.log
echo "rc=${PIPESTATUS[0]}" >> Transient/live/river/ext_river.log
