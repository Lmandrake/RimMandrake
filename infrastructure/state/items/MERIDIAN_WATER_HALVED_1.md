## spec
✅ **OWNER, 2026-08-22 13:04:** *"I would like to shrink the meridian water bodies to around
half their current size."*

⛔ **QUEUED, NOT STARTED.** The owner ruled in the same breath: *"only after we've closed out
anything that affects the next game reload."* Do not begin this until the reload work is done.

## scope
Meridian water = the water bodies at arc > 82. **The Grey Sea** is the main one — gazetteer
(92, 8), 0 m sink, already described as *"salt-encrusted, shrinking"*. Establish the full
list from `world/ASHKARR_WORLDMAP_tiles.csv` (`water` column, `elev_m`, `arc`) before
touching anything; do not assume the Grey Sea is the only one.

Target: **~50% of current tile count**, shrinking from the margins inward so the retained
core sits at the lowest elevations. Pair it with `GREY_SEA_BRINE_PATCHES_1`, which puts the
remnants back as scattered brine — the two are one gesture and should land together.

## 🔴 canon moves with this, and it must move in the same change
`canon.yml > planet.water_pct` reads **8.14% / 1,780 tiles**. Halving meridian water changes
that number. **Re-measure and update canon in the same commit**, or the next audit reports
this ruling as a defect.
⚠️ `planet.status` is currently `remaking`, so planet rules are advisory and will not block
the write — that is not permission to leave canon stale.

## the engine constraint that governs the edit
`SurfaceTile.WaterCovered => elevation <= 0f`. **A tile is water because of its elevation**,
not because of a biome label. This is the rule that forced the Scald from +1411 m to −30 m
(`SCALD_WATER_RULING_1`, `bd5dad0`). ⇒ Un-watering a tile means raising it above 0 m; a biome
change alone will not do it, and doing only the biome leaves an invisible sea.

## verify
Render it and LOOK — `worldview.py`. The owner's method is the picture, not the number
(`CLAUDE.md`: *"a number that says the world is fine while the picture shows compass circles
is the number being wrong"*). Then: meridian water tile count ~half its pre-pass value,
no water tile left above 0 m, `canon.yml` updated, and no river created at arc > 74 (§4 rule 7
forbids terminator rivers outright).

## criteria
Meridian water ≈50% of current, canon re-measured, the result approved by looking.
