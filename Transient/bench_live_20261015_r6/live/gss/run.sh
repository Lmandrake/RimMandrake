#!/bin/bash
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261015_r6
timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots 2>&1 | tr -d '\r' > Transient/live/gss/gss_fogguard_$1.log
echo "rc=${PIPESTATUS[0]}" >> Transient/live/gss/gss_fogguard_$1.log
