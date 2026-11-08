#!/bin/bash
# reshoot.sh <save> <tag> <looks>: load a bars3 save on game A and shoot the looks again (origin from the last b3_origin file)
python.exe -c "
import sys; sys.path.insert(0,'ralph/live'); import fwb; B=fwb.FW(); B.call('rimworld/load_game', saveName='$1'); print(fwb.V._wait_playing(B))"
read -r _ _ _ OX OZ < Transient/ralph_fw/b3_origin_p3a.txt
python.exe ralph/live/bars3.py shoot $OX $OZ $2 $3 > Transient/ralph_fw/b3_shoot_$2.out 2>&1
echo shot $2
