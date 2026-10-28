# DUGSWIM_TAME_RAIN_FLIP_BURST

## spec
Live r17 (D:\ClaudeWork\rimmandrake\bench_live_r17\PROGRESS.md, prof_RAIN_B2_ON.txt, prof_RAIN_A2_ON.txt, prof_RAIN_C_A.txt):
in rain on map1 (325x325, ~80k dug squares, 100 rigs) RM_MapComponent_Excavation.RefreshDugSwim (RM_MapComponent_Excavation.cs ~410)
takes 44-55 ms in ONE tick (B2 max 54.7, A2 max 50.1, C_A 44.0; mean ~2.3-2.7 ms over ~70-136 calls / 2-4k ticks).
It is the whole rain-window max of the Excavation component (bar <20 ms). Cause read from source: full depthGrid walk, then for every
square whose swim state flipped it calls map.pathing.RecalculatePerceivedPathCostAt, plus BumpCells + reachability.ClearCache — a rain
pass flips thousands of squares at once.
Fix bar: re-run r17 RAIN windows; RefreshDugSwim max <5 ms and Excavation map1 max <20 ms in rain, swim state still converges
(SWIMGRID unnamed 0). Likely: budget the changed-square list across ticks (like TerrainWriteBudget) and/or skip the full walk by tracking changed indices.
