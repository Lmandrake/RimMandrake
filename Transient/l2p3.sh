#!/bin/zsh
cd /home/mandrake/rm/foundry
m=$1
python.exe Transient/l2p3_reset.py $m 2>&1 | tail -1
s=$(date +%s)
timeout ${2:-540} python.exe Transient/l2sweep_run.py $m > Transient/l2p2_$m.log 2>&1
echo "$m exit $? after $(( $(date +%s)-s )) s"
python.exe Transient/l2p3_reset.py $m 2>&1 | tail -1
python3 - <<P
import json
try:
    d=json.load(open("Transient/l2sweep_$m.json"))
    print("keys",list(d)[:12]); print("all_green",d.get("all_green"),"err",d.get("error"))
except Exception as e: print("nojson",e)
P
