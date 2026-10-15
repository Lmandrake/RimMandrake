# TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA

Filed by BENCH 2026-10-15 (live round 7, HEAD 0207ac8fc2). Evidence in `Transient/bench_live_20261015_r7/live/`:
`river/river_site.log`, `river/ext_swept_site1_{1,2,3}.json` and `.log`, `probes/edge_probe.py`, `probes/maps_probe.py`.
Class SITE/HARNESS. Both defects are in `src/RimMandrake/FlowWorks/northstar/river_site.py`, and the swept row consumes them.

## 1. The swept row was staged on a river that has no downstream map edge

`river_site.py` (run on the r6 Pyrelands fixture's world) settled on a map with a fast lane. On that map:
- moving water reached exactly ONE edge: north z=249, 14 cells. South, west and east had 0 (`edge_probe.py`);
- the river ends in the ocean (the z=0 row is WaterOcean*, which is not "Moving").

`extensions_rivers.swept` stages throwaway colonists on edge river cells. All 5 landed on the north (inflow) edge, so nobody could
be carried off. Two runs read `returns_home` UNMEASURED: "5 colonists stood on moving water at the map edge ... for 1500 ticks
and none was washed away". The docstring of `edge_river_cells` already expects an upstream run. The site check only asks
`ProofGrid` for `current > 0 and fast > 0`, which never tells you whether the river leaves the map.

**Guard (to build).** `river_site.py` accepts a tile only if moving water reaches at least two map edges. Otherwise it
needs the mod's flow map to show a downstream edge. `swept` should say UNMEASURED/SITE "no downstream edge" up front, instead
of waiting 1500 ticks.

A fresh quicktest world (tile 248: moving water on 3 edges) PASSed the swept row 3 out of 3 times.

## 2. river_site passes a Find.Maps INDEX where set_current_map wants a uniqueID

`river_site.py` L198 calls `jawa/set_current_map(mapId=g["mapIndex"])`, but `jawa/world_tile_map_generate` documents `mapId`
(Map.uniqueID) as the stable id and `mapIndex` as a position that shifts. On the fixture world the uids were 1..10 at indexes
0..9 (`maps_probe.py`). So every candidate's `ProofGrid` line was printed under the NEXT tile's number. The site it settled was
tile 60145 (uid 9), not the 60146 it reported, and the rejected candidate maps stayed loaded. On a fresh quicktest (home map
uid 0 = index 0) the two agree, which is why this went unseen.

**Fix.** Use `g["mapId"]`, and drop rejected maps for every reject reason, not only scenery.

## also seen, same run

- Swept run 1 on that site was stopped by `hostile_arrival: arrived: AA_Bumbledrone (animal)`
  (TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ).
- Starting a quicktest and generating a river map before the quicktest reached Playing broke the map generation: GenStep
  "Collection was modified", programState stuck at MapInitializing, and `extension_proof`'s `ensure_playing_map` then hung in
  `prove_quicktest_world.py`. That was the driver's own error (`river_site_2_concurrent_mapgen.log`). Always wait for Playing +
  `map_info` first (`probes/fresh_map.py`).

## verify

Run `river_site.py` on a world whose first fast-lane tile's river ends at the sea. It must reject that tile. Then run
`extension_proof --live --site river --chains swept` and expect PASS. Its printed tile must equal `jawa/map_info` tile.
