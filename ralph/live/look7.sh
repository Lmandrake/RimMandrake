#!/bin/bash
# look7.sh <tag>: pass 7's one look sitting on a fresh quick-test map at 11:00, all at the owner's play zoom (root 7.2, ~64 px):
# the depth sheet (default look only, occupied 3x3 pits at 4 m and 8 m), the graded-trench walk, then ladders/portables/gear.
python.exe ralph/live/fresh.py --hour 11 > Transient/ralph_fw/fresh_l7_$1.out 2>&1
S=$(grep -o 'SHIFT=[-0-9,]*' Transient/ralph_fw/fresh_l7_$1.out | cut -d= -f2)
DX=${S%,*}; DZ=${S#*,}
OX=$((140 + DX + 6)); OZ=$((139 + DZ - 22))
echo "shift $S origin $OX $OZ" | tee Transient/ralph_fw/l7_origin_$1.txt
python.exe ralph/live/bars3.py stage $OX $OZ > Transient/ralph_fw/l7_stage_$1.out 2>&1
python.exe ralph/live/bars3.py shoot $OX $OZ $1 1 > Transient/ralph_fw/l7_shoot_$1.out 2>&1
python.exe ralph/live/walk7.py $((OX - 14)) $((OZ + 2)) > Transient/ralph_fw/l7_walk_$1.out 2>&1
B2_ZOOMS=7.2,11 WSLENV=${WSLENV:+$WSLENV:}B2_ZOOMS python.exe ralph/live/ladders5.py rig portable gear > Transient/ralph_fw/l7_ladders_$1.out 2>&1
python.exe ralph/live/fwb.py call rimworld/set_time_speed '{"speed":"Paused"}' > /dev/null
echo done
