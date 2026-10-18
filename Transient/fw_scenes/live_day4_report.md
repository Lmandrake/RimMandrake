# FlowWorks live day 4 — FOUNDRY, 2026-10-18 03:05-03:45Z

Bridge taken 03:05Z (bridge_calls quiet since 02:17Z), released 03:45Z. 11-mod flowworks list throughout.

## validation_v2 after the triage (c38ffbe8e, 33461177a: python only)
- Calm site v1, DLL 71aaadd97: **46 PASS / 9 FAIL / 6 UNMEASURED** (`live/day4/v2_calm_stdout.txt`). Every flow row the
  triage marked (a)/(b) now passes. Left: the whole pawn block (E4_engine_off, E7a, E7b, E8, P1, P3f, P4, P4f, P4b,
  P5n, X2, X3, X4), E6_rain (cascade of the unfinished E7a dig) and E9.
- **Root cause of the pawn block = the saved test map, not the mod.** `RM_TestSite_calm_v1` was saved on a 22-mod
  list. Loaded on the 11-mod list (ignoreModCompatibility) it logs ~9,900 "Could not load reference to Corpse_RSW_* /
  Corpse_RM_*" and then `Root level exception in Update(): NullReferenceException at Verse.MapDrawer.WholeMapChanged`
  every frame (8,876 times in `live/day4/Player_after_v2_calm.log`, line 10084 on). The update loop throws each frame,
  so `step_game_ticks` completes 0 ticks (E4: 0 of 309) and no pawn job advances. E9's new top-lines list named it.
- `--fresh-map` aborted 4 of 4 on "not pristine: bodies 21..28": P11 forms every natural body at map load, so the
  harness's `bodyCount == 0` pristine test is stale. Fixed in validation_v2.py L1 and in test_site_saves.py's roll check
  (pristine = nothing dug). Then on fix3 DLL 6699957b8: **`--fresh-map` 61/0/0** (`validation_v2_result_20261017T202014.json`).
- Test map remade: `test_site_saves.py build calm` -> **RM_TestSite_calm_v2** (built on the 11-mod list; v1 kept,
  copy `RM_TestSite_calm_v1.before_fw11_rebuild_20261018.rws`). **Calm v2: 61/0/0**
  (`validation_v2_result_20261017T203750.json`, `live/day4/v2_calm2_stdout.txt`).

## fix3 proofs (DLL 6699957b8, source 47b1a5045)
- Swim (`live/day4/proofs_swim_fix3.json`): **dug 3 m reservoir now swimmable** (deepCell=True pathCost=60, reached,
  far side reached), mechanoid refused at the dug reservoir and the natural lake, natural-lake rows, warning, animal
  round, toggle off/on PASS. Prisoner in a flooded pit PASS after a staging fix: with shipped rain fill a 3.5 m hole with
  2 m water rose to 2.5 m in 1,500 ticks (a K 2 step) and the prisoner climbed out by the rule (SITE); the pit is now
  4 m deep. Drafted-under row UNMEASURED (the drafted target is the lake's edge row: exit in reach; day 3's mid-lake
  hand trace drowned in ~1 h).
- Sweep (`live/day4/sweep_identity_fix3.json`): prisoner and slave are now BOOKED (pending 2) and come back as
  themselves on paper (same ThingID, faction, guest status Prisoner / Slave). **Slave PASS, back on the map.**
  **Prisoner FAIL: "Back from the river: Bear" letter fired (returned on an edge cell), but within 10 ticks it was off
  the map, and later not spawned, not held, not a world pawn.** Likely mechanism (not proven): the return cell is a
  map-edge cell and vanilla prisoner escape exits from an edge at once; the escape guard covers current lanes only.
  Colonist and tame animal were not swept on this site (weak current: colonist walked out, downed muffalo stayed).
- S3 (`live/day4/run_S3_fix3_stdout.txt`): **S3.c MATCHES** — pond lost 60,000 dL = canal 60,000 dL + hoses 0, no
  spill, overflowDestroyed 0 (day 3: 9,750 dL lost).
- S5 rerun: not done — the painted-pond floor pin (deepBedsEnabled off while staging) is in validation_v2 but not yet
  in water_scenes_walk.py.
