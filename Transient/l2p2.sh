#!/bin/zsh
cd /home/mandrake/rm/foundry
m=$1
timeout ${2:-500} python.exe Transient/l2sweep_run.py $m > Transient/l2p2_$m.log 2>&1
echo "$m exit $?"
