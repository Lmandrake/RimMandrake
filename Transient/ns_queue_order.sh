#!/bin/bash
cd /mnt/d/Luke/dev/wt_live2
echo "=== J1bw $(date +%H:%M:%S)"
python.exe -u src/RimMandrake/Utils/modcheck/live_queue/j1_situational_rerun.py --bland-world 2>&1 | tail -40
echo "=== J1 done $(date +%H:%M:%S)"
echo ALLDONE
