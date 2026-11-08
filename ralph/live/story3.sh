#!/bin/bash
# story3.sh <points> <faction> <tag>: a fresh quick-test map, the story layout round the colonists, a raid, a watch (runs on Steve)
set -x
python.exe ralph/live/fresh.py --hour 9 > Transient/ralph_fw/fresh_$3.out 2>&1
S=$(grep -o 'SHIFT=[-0-9,]*' Transient/ralph_fw/fresh_$3.out | cut -d= -f2)
echo "shift $S"
export FW_SHIFT=$S FW_ROOT=${FW_ROOT:-20} WSLENV=${WSLENV:+$WSLENV:}FW_SHIFT:FW_ROOT
python.exe ralph/live/story1.py stage --d 4 > Transient/ralph_fw/stage_$3.out 2>&1
python.exe ralph/live/story1.py raid --points $1 --faction $2 > Transient/ralph_fw/raid_$3.out 2>&1
python.exe ralph/live/story1.py watch --ticks 30000 --slice 240 --every 1 --wall 2400 > Transient/ralph_fw/watch_$3.out 2>&1
python.exe ralph/live/fwb.py call rimworld/set_time_speed '{"speed":"Paused"}' > /dev/null
echo done
