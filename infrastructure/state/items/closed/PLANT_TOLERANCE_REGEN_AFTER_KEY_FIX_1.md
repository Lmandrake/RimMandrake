# PLANT_TOLERANCE_REGEN_AFTER_KEY_FIX_1 — regenerate + deploy the widened patch

## why

`PLANT_TOLERANCE_VERIFY_STALE_CLIMATE_KEYS_1` fixed `plant_tolerances.py`'s
`sheet_demands()`/`verify()` to resolve a biome's live defName through
`design/Jawa/worldbuilding/biomes/rosters/*.json` instead of a stale, pre-rename
`biome_climate.json` key. That fix changes `compute()`'s output, not just `verify()`'s
report: 19 of 20 biomes now pick up a real sheet-median demand for the first time, so the
currently-deployed `src/RimUtinni/UtinniPatches/Patches/PlantTolerances_Ashkarr.xml`
(written under the old, silently-narrower `sheet_demands()`) under-widens plants against
their biome's sheet median for every biome except Pyrelands.

## spec

Re-run `python3 design/Jawa/mods/plant_tolerances.py --write`, review the diff against the
currently-deployed patch (expect wider bounds, never narrower — WIDEN ONLY still applies),
then run it through the normal deploy path (`rimworld-deploy` skill /
`deploy_custom_mods.py`) so the live Mods folder actually carries it.

## verify

`git diff --stat src/RimUtinni/UtinniPatches/Patches/PlantTolerances_Ashkarr.xml` shows a
real change, `plant_tolerances.py` still prints `✅ ... grow at their biome's sheet median`
afterward, and the deployed copy matches the repo copy (`validate_patch.py --live`).

## criteria

The deployed `PlantTolerances_Ashkarr.xml` reflects `compute()`'s output under the fixed
`sheet_demands()`, not the pre-fix one.
