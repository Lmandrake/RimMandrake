## spec
Plan P1 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`).
Deploy the `fe309aefe` FlowWorks DLL (dry-front creep fix, game down), rerun S2, S5 and S6 of
`src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py`, record with modcheck. This is a BASELINE of today's kernel,
before the P3 solver replaces it; it does not prove level water. Do `WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4` first (the
2026-10-17 walk stopped with tracebacks after S4.c and in S5). Previous run: `Transient/fw_scenes/live/`.

## verify
- L2: S2 fills with every pulse within one level of its neighbours (no [4 0 4 0] pattern), state read.
- L2: S6 save/reload ends in the same totals and end state as the never-saved run (owner S6.Q1 = b).
- L2: S5 runs to the end and reports every row (its whole-notch rows are expected to disagree with level water;
  record them as the baseline, not as a pass or a fail of the rebuild).
- The run is recorded with `modcheck record` and the result path is noted here.
