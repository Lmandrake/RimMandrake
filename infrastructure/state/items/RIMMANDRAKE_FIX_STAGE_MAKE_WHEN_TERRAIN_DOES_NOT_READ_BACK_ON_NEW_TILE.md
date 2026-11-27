# RIMMANDRAKE_FIX_STAGE_MAKE_WHEN_TERRAIN_DOES_NOT_READ_BACK_ON_NEW_TILE

## spec
`stage_map.py make ArchSmall --kind settlement` refused on 2026-11-25 03:50 PST (tile 113515, AridShrubland): set_terrain_batch
painted 10000 cells and 619 did not read back. `empty_map` in `src/RimMandrake/Utils/stage_map.py` paints one terrain with no
`clearOverlays`. TerrainAt reads floodwater/thin ice (tempGrid) and Substructure (foundation) before the top grid, so a bare paint
leaves those cells showing. `validation_core._prepare_site` already passes `clearOverlays: True` for this cause
(HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK, 7501ea37f3). The fix: `empty_map` passes `clearOverlays: True` too.

## verify
Offline: `python3 src/RimMandrake/Utils/selftest_stage_map_terrain.py` (the empty_map terrain call carries clearOverlays).
Live: the same make on a fresh tile exits 0 and prints MADE settlement stage.

## criteria
- empty_map's set_terrain_batch call passes clearOverlays=True (offline selftest).

## refs
file: src/RimMandrake/Utils/stage_map.py
