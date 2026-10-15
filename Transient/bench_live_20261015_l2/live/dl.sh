#!/bin/bash
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261015_l2
export RM_ALLOW_CONCURRENT_BRIDGE=1 WSLENV=RM_ALLOW_CONCURRENT_BRIDGE
L=Transient/live
timeout 600 python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load calm 2>&1 | tr -d '\r' | tail -3 > $L/dl_load.log
timeout 1800 python.exe src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_l2\\Transient\\live\\deep_lake_1.json" 2>&1 | tr -d '\r' > $L/deep_lake_1.log; echo "rc=${PIPESTATUS[0]}" >> $L/deep_lake_1.log
timeout 900 python.exe Transient/live/dl_save_reload.py 96,96 "D:\\Luke\\dev\\_rmscratch\\bench_live_20261015_l2\\Transient\\live\\deep_lake_reload_1.json" 2>&1 | tr -d '\r' > $L/deep_lake_reload_1.log; echo "rc=${PIPESTATUS[0]}" >> $L/deep_lake_reload_1.log
echo DL_DONE >> $L/deep_lake_reload_1.log
