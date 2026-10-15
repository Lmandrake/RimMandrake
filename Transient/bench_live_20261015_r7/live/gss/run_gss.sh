#!/bin/bash
cd /mnt/d/Luke/dev/_rmscratch/bench_live_20261015_r7
timeout 1200 python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots 2>&1 | tr -d '\r' > Transient/live/gss/gss_fogguard2_$1.log
echo "rc=${PIPESTATUS[0]}" >> Transient/live/gss/gss_fogguard2_$1.log
grep -E "P2c_|P3_|ABORTED|NOT PASS|GOVERNOR_STOP|^  -> |TOTAL|PASS:" Transient/live/gss/gss_fogguard2_$1.log | cut -c1-300 | tail -n 25
tail -n 1 Transient/live/gss/gss_fogguard2_$1.log
