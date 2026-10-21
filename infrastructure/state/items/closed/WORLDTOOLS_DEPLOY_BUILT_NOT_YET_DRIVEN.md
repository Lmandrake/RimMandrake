# WORLDTOOLS_DEPLOY_BUILT_NOT_YET_DRIVEN

Deploy the JawaBench companion carrying the world-tools review fixes (commits 47cd70f8e + be8bc721b) at the next
game shutdown, then smoke-test the changed tools live.

- Review that found the defects: `Transient/review_JawaBenchWorldTools_2026-10-20.md` (D1-D9).
- Source: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs`, new pure helper
  `JawaBenchWorldArgsCore.cs` (offline units: `python3 src/RimMandrake/Utils/selftest_world_args_core.py`, 43/43).
- Built to staging with `build.py --gm` (0 warnings, 0 errors); tool surface unchanged at 410 `jawa/` names
  (UTF-8 + UTF-16 scan, identical to the deployed DLL). NOT deployed: the game was running.

## Deploy
`taskkill.exe` the game, `python3 src/RimMandrake/bridgetools/build.py --gm --apply`, check for `deployed`.

## verify
Live smoke list (quicktest world, read results, not `success`):
1. `world_tile_get range=0-2147483647 limit=3` returns at once; errors[] names the clip to 0..TilesCount-1.
2. `world_tile_set tiles=5 elevation=NaN` refused, tile 5 unchanged (read back with world_tile_get).
3. `world_links_set path=14,abc,7368` refused, nothing laid.
4. `world_links_clear tiles=A,B to=C` refused, links on A and B still present.
5. `world_links_clear` on a tile with no links: success=true, nothingRemoved=true.
6. `world_objects_set ids=<id>` with no field refused; with the same tile it already has: changed=0, unchanged=1.
7. `world_features_set action=rename featureId=<id>` refused; `action=create def=Region tiles=abc` refused and
   world_features_get shows no new feature; `centerOnTile=99999999` refused.
8. `world_info_set` with no args refused; `pollution=NaN` refused.
9. `world_tile_import` on a CSV with a `NaN` elevation cell: badCells=1, success=false, tile unchanged.
10. `world_links_import clearFirst=true apply=true` on a CSV with one unknown def: refused, existing links intact.
11. `world_mutators_set action=add mutators=Caves,NoSuchDef tiles=5`: success=false, unknownDefs=[NoSuchDef].
12. `world_features_import clearExisting=false apply=true` on a correct CSV over an already-labelled planet:
    success=true, tilesReassigned > 0.
