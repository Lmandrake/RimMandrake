#!/bin/bash
# run.sh <tag> : one sc_moat_raid run, evidence to the sitting folder; prints rc and the row statuses
S=/mnt/d/ClaudeWork/rimmandrake/testpilot_pit_capture_faults
t0=$(date +%s)
timeout 500 python.exe -u src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_moat_raid --out "$(wslpath -w $S/$1.json)" > $S/$1.log 2>&1; rc=$?
echo "rc=$rc secs=$(( $(date +%s) - t0 ))"; tail -n 3 $S/$1.log | cut -c1-400
python3 $S/rows.py $S/$1.json t
