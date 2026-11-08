#!/bin/bash
# look4.sh: load the fw3_bars save on game A and run bars4 east of the depth rows
python.exe -c "
import sys; sys.path.insert(0,'ralph/live'); import fwb; B=fwb.FW(); B.call('rimworld/load_game', saveName='fw3_bars'); print(fwb.V._wait_playing(B))"
read -r _ _ _ OX OZ < Transient/ralph_fw/b3_origin_p3a.txt
python.exe ralph/live/bars4.py $((OX + 25)) $OZ $@ > Transient/ralph_fw/bars4.out 2>&1
python.exe ralph/live/fwb.py call rimworld/save_game '{"saveName":"fw3_look4"}' > /dev/null
python.exe ralph/live/fwb.py call rimworld/set_time_speed '{"speed":"Paused"}' > /dev/null
grep -E "covers|walker|ProofLadder|ProofBuild|SHOT|b2_" Transient/ralph_fw/bars4.out | cut -c1-220
