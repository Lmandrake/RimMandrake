# PLANT_TOLERANCE_VERIFY_STALE_CLIMATE_KEYS_1 — plant_tolerances.py's own safety net has been silently vacuous

## the gap, MEASURED 2026-09-20

`design/Jawa/mods/plant_tolerances.py --write` prints `✅ all 0 landed flora rows grow at
their biome's sheet median` — that `0` is the total ROWS CHECKED, not a pass count, and
its own docstring says the check "must print 0 [dead]", not 0 total. `verify()` looks up
each biome in `design/Jawa/worldbuilding/review/biome_climate.json['biomes']`, keyed by
names like `"Desert"`, `"ExtremeDesert"`, `"AridShrubland"` — pre-tier-rename short names —
while `biome_flora.py`'s `FAMILIES` (and every live BiomeDef) key by `RUT_Desert`,
`RUT_ExtremeDesert`, `RUT_AridShrubland`. Every lookup misses, `med is None`, every row is
skipped via `continue`, `total` stays 0, and the function trivially reports success.

**Found incidentally** while regenerating `PlantTolerances_Ashkarr.xml` for
`BMT_FLORA_ABSORPTION_1` (3 new plants).

🔴 **CORRECTED 2026-09-20 (was wrong when first written):** `sheet_demands()` — the WRITE
path's own second demand source — does the identical `clim.get(b)` lookup as `verify()` and
carries the SAME bug, not a separate one. Of the 20 biome keys `FAMILIES` actually uses, only
`ZBiome_Grasslands` already matched `biome_climate.json` verbatim; the other 19 (`RUT_Desert`,
`RUT_Wasteland`, `RUT_ForsakenCrags`, ...) all missed, so `compute()`'s "union of tile-CSV and
sheet-median demand" was silently just the tile-CSV demand for every biome except Pyrelands.
The 85-operation patch written this session was **not** unaffected — it under-widened every
plant whose sheet median sat outside its tile-derived band, for 19 of 20 biomes.

## why this matters

`verify()`'s own docstring: "A generator that only reports what it wrote cannot tell you
whether the defect is closed... it must print 0" — i.e. this check exists specifically so
a plant that got mis-fit to a climate it cannot survive is caught before the patch ships.
Right now nothing is checked, at all, for any of the 85 rows this script touches.

## spec

`biome_climate.json`'s `biomes` keys need to match the live `RUT_`/`AB_`-prefixed
defNames `FAMILIES` and the BiomeDefs actually use — either re-extract it from the sheet
`.md` files with today's tier-prefixed names, or write a name-mapping table if the sheets
themselves still use short names. Re-run `plant_tolerances.py` afterward and confirm
`total` lands near 85 (one row per landed flora assignment) with a real dead-row list
before trusting `✅` again.

## verify

`python3 design/Jawa/mods/plant_tolerances.py` prints a `total` count that is not 0 and
plausibly close to the ~150 flora assignments `biome_flora.py --check` reports.

## criteria

`verify()`'s dead-row check actually inspects every landed flora row instead of skipping
all of them.
