#!/bin/bash
# story5.sh <points> <faction> <tag> [spawn]: raid + watch on the map story3 already staged (runs on Steve)
S=$(grep -o 'SHIFT=[-0-9,]*' Transient/ralph_fw/fresh_${FW_STAGE:-$3}.out | cut -d= -f2)
export FW_SHIFT=$S FW_ROOT=${FW_ROOT:-20} WSLENV=${WSLENV:+$WSLENV:}FW_SHIFT:FW_ROOT
python.exe ralph/live/story1.py raid --points $1 --faction $2 ${4:+--spawn $4} > Transient/ralph_fw/raid_$3.out 2>&1
python.exe ralph/live/story1.py watch --ticks ${FW_TICKS:-30000} --slice 240 --every 1 --close ${FW_CLOSE:-0} --wall ${FW_WALL:-2400} > Transient/ralph_fw/watch_$3.out 2>&1
python.exe ralph/live/fwb.py call rimworld/set_time_speed '{"speed":"Paused"}' > /dev/null
echo done
