# MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED

`MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED` — plan built offline and committed; NEXT: with the bridge held, run `python.exe world/_mountain_apply2_2026-10-20.py world/ASHKARR_MOUNTAINS2_2026-10-20_plan.json <outdir>` on a loaded `ASHKARR_DEV_START_2026-10-20_RECORDLINKS`, then rerun with `--apply` once it reports 0 mismatches.

## What
Write the second mountain pass live: 805 hilliness and 4 elevation tiles, via grouped `world_tile_set` and one `world_commit`. Then save as `ASHKARR_DEV_START_2026-10-20_MOUNTAINS2.rws`, never over the base.
Design, numbers and the steps: `design/Jawa/worldbuilding/mountain_system_2026-10-20.md` §Second pass.

## Verify
- Before writing, live hilliness must equal the plan's `before`, and elevation must equal `elevationBefore`, with 0 mismatches. If not, the base has moved: stop and regenerate.
- The read-back after the commit must show 0 mismatches.
- Predicted `world_lint`: 21 → 21. Only "settlement on Impassable" reads hilliness.
- Read the saved file offline: biomes, the 326 river links, the 1,242 road links and the 97 settlements must be unchanged.
- `python3 src/RimMandrake/Utils/selftest_mountain_plan2.py` must pass.
- The owner looks at the globe. That is the acceptance test.

## Watch out
- The base must load as `TidallyLocked`.
- VEF "New faction" dialogs pop up on load (answer *Do nothing*).
- The plan's `save` key names RECORDLINKS. A newer world edit since 10:50 2026-10-20 means the `before` values are stale.
