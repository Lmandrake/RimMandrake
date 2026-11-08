#!/bin/bash
# bars3.sh <tag> [looks]: a fresh quick-test map at 11:00, the depth contrast rows south-east of the colonists, every look shot
python.exe ralph/live/fresh.py --hour 11 > Transient/ralph_fw/fresh_b3_$1.out 2>&1
S=$(grep -o 'SHIFT=[-0-9,]*' Transient/ralph_fw/fresh_b3_$1.out | cut -d= -f2)
DX=${S%,*}; DZ=${S#*,}
OX=$((140 + DX + 6)); OZ=$((139 + DZ - 22))
echo "shift $S origin $OX $OZ" | tee Transient/ralph_fw/b3_origin_$1.txt
python.exe ralph/live/bars3.py stage $OX $OZ > Transient/ralph_fw/b3_stage_$1.out 2>&1
python.exe ralph/live/bars3.py shoot $OX $OZ $1 ${2:-0,1,2} > Transient/ralph_fw/b3_shoot_$1.out 2>&1
python.exe ralph/live/fwb.py call rimworld/set_time_speed '{"speed":"Paused"}' > /dev/null
echo done
