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

## guard built (BENCH 2026-10-15, offline; `Transient/experiment_2026-10-14/testenv_hardening_3.md`)

- `extensions_rivers.moving_edges()` counts moving river water per map edge. `MIN_RIVER_EDGES` = 2.
- `river_site.py` changes:
  - It accepts a RIVER tile only when `river_reject()` says None: a current, a fast lane, and moving water on 2 or more
    edges. Unreadable edge terrain rejects the tile.
  - It reads the current map's tile back against the candidate (`map_info.tile`).
  - It calls `set_current_map` with `generated_map_id(g)`, which is `mapId` (Map.uniqueID). It never uses `mapIndex`,
    and a missing id is a refusal.
  - Every rejected candidate map this run generated is removed, for every reject reason.
- `swept` says `UNMEASURED: SITE: no downstream edge` up front, staging nobody and waiting no ticks, when fewer than 2
  edges carry moving water. It no longer waits 1500 ticks. What the row measures on a valid site is unchanged.
- Offline checks that can go red:
  - `selftest_river_site`: the r7 sea-ending shape counts 1 edge, and `edge_river_cells` alone would still accept it
    (can-fail). `river_reject` cases. `main()` runs against a fake world whose map uids differ from their indexes: the
    sea river is rejected and its map removed, and set_current_map gets uids. Mutations went red: mapIndex 7 checks, no
    edge rule 6 checks, no drops 3 checks.
  - `selftest_extensions`: swept on the sea shape is UNMEASURED up front. Mutation: PASS, staged 3.

## live proof (next round)

```
timeout 900 python.exe src/RimMandrake/FlowWorks/northstar/river_site.py 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\river_site.log"
timeout 1800 python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --chains swept --out "D:\Luke\dev\_rmscratch\<round>\ext_swept_<n>.json" 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\ext_swept_<n>.log"
```
Run river_site on the r6 Pyrelands fixture's world: tile 60146 must be printed `rejected: no downstream edge`.
- Bar: the final `tile T mapId U map_info tile T` line has equal tiles, and `loaded maps:` shows no other candidate
  tile.
- swept x3 then reads returns_home PASS.
