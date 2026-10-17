## spec
`src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py` on the 2026-10-17 live walk
(`Transient/fw_scenes/live/walk_S2_S6_summary.txt`): after S4.c the summary prints "Traceback (most recent call
last):" with no rows for S4.d, and again inside S5 with no S5 rows; S6 then ran. The traceback bodies were not kept, so
the first step is a `--mock`/offline reproduction. Independent bug; blocks P1 (`WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX`).

## verify
- L1: the walk's mock run reaches the end of S4 and S5 and prints every row; a crash in one scene prints its traceback
  in full and the walk continues to the next scene.
