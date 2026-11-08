#!/bin/bash
# replay.sh <save> <ticks> <tag>: load a save on game A, then story1 watch (runs on Steve)
python.exe -c "
import sys; sys.path.insert(0,'ralph/live'); import fwb; B=fwb.FW(); B.call('rimworld/load_game', saveName='$1'); print(fwb.V._wait_playing(B))"
python.exe ralph/live/story1.py watch --ticks $2 --slice 240 --every 3 > Transient/ralph_fw/watch_$3.out 2>&1
