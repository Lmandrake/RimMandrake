# WB-item-RIMMANDRAKE-READ-FIX-70846FF57A-WITH-FRESH-EYES-20261127-161439

Member: `RIMMANDRAKE_READ_FIX_70846FF57A_WITH_FRESH_EYES`, a fresh read of `src/RimMandrake/Utils/stage_map.py` after the
fix 70846ff57a (empty_map paints its one terrain with `clearOverlays=True`).

## Group 1 (the one member): read, nothing significant

- The file has no boundary page (`code_review_status.py check` reads NO PAGE). It was read against its docstring and the
  fix's spec (`infrastructure/state/items/RIMMANDRAKE_FIX_STAGE_MAKE_WHEN_TERRAIN_DOES_NOT_READ_BACK_ON_NEW_TILE.md`).
- The fix: `clearOverlays` is the parameter name that `JawaBenchTerrainTools.cs` (line 244) reads. A failed read-back
  comes back as `success: false`, so `must` refuses the make. The make does not save a bad stage.
- The test `selftest_stage_map_terrain.py`: PASS on the real file. FAIL on a copy with `clearOverlays=True` removed
  ("empty_map's set_terrain_batch has no clearOverlays=True").
- Not significant, no ticket: `pick_tile` scans only tiles below the green room's tile. A home tile under 60 makes a range
  such as `0--1`. The make then refuses by name ("no flat settleable tile"). No concrete case seen.
- Record: `code_review_status.py mark-clean src/RimMandrake/Utils/stage_map.py` (CLEAN at 78e8283f9d);
  `fresh_reader.py holds 70846ff57a src/RimMandrake/Utils/stage_map.py` exits 0.
- Context after the group: small; no restart.
