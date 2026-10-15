#!/bin/bash
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261015_l2
export RM_ALLOW_CONCURRENT_BRIDGE=1 WSLENV=RM_ALLOW_CONCURRENT_BRIDGE
L=Transient/live
timeout 1800 python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --out "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_l2\\Transient\\live\\ext_river_1.json" 2>&1 | tr -d '\r' > $L/ext_river_1.log; echo "rc=${PIPESTATUS[0]}" >> $L/ext_river_1.log
timeout 1800 python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site dry --site-save calm --chains fuel_moat_chemfuel,fuel_moat_astrofuel --out "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_l2\\Transient\\live\\ext_fuel_1.json" 2>&1 | tr -d '\r' > $L/ext_fuel_1.log; echo "rc=${PIPESTATUS[0]}" >> $L/ext_fuel_1.log
echo EXT_DONE >> $L/ext_fuel_1.log
