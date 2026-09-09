# comparator_sheet.png (v3) -- caption legend

MAPGEN_PAINTER_V1_1 round 3. Same 8 plans, same sheet/seeds as v0/v1/v2
(`Transient/mapgen_v0/`, `Transient/mapgen_v1/`, `Transient/mapgen_v2/`);
repainted by `mapgen_paint.py` after one fix: point hydrology
(spring/brine_seep/salt_pan) on a carved-line landform (Canyon/Gorge/
Badlands/Rift) used to stamp dead-centre on the channel's own centreline,
which is exactly where the channel's terrace bands hit their rock/
roughhewn threshold -- most of the stamp then failed the IMPASSABLE_ROCK
write-guard. Round 2's grade called this "hydrology dressing too small to
read"; measuring it directly (not by eye) found real cell counts of
493-534 Marsh cells per affected seed already, not a token handful -- the
true defect was the stamp sitting inside rock, not its nominal size. Fix:
`_channel_bank_point()` (new helper) offsets the stamp perpendicular onto
the channel's own gravel/mud bank, clear of rock, and the raised_blob
case (`_point_hydrology`'s spring/brine_seep, exercised by no seed in this
8 but same bug for a LoneMountain) gets the equivalent push away from its
rock core. Effect on this sheet: brine_seep Marsh cells roughly double
(493->974, 530->966, 534->1007 on seeds 1/3/8) and read as a visible green
patch on the sheet at thumbnail scale, not just in the raw grid.

Same 5 corpus crops as v1/v2, for a like-for-like comparison.

## measured (corpus_stats.py, 250-bucket band from corpus_map_stats.md)

|              | v2 (round 2) | v3 (round 3) | corpus 250-bucket band |
|---|---|---|---|
| distinct_terrains | 10-12 | 10-12 | (target: >=10, the item's own gate) |
| perim_area_mean | 2.632-2.893 | 2.632-2.884 | 2.619-3.064 |
| region_size_max_frac | 0.065-0.285 | 0.068-0.208 | 0.044-0.635 |
| region_count | 128-547 | 228-761 | 496-3056 |

selftest (mapgen_v0.py --selftest): 5/5 PASS -- variety, validate, defnames,
distinct_terrains (>=10 all 8), perim_area (2.4-3.3, >=6/8: 8/8 in-band).
gates.json: 8/8 connectivity/buildable-area PASS. Region-shape stats are
essentially unchanged from round 2 (this fix only touches a small point
feature, not the macro terrace pass round 2 fixed) -- expected, and not a
regression: round 2's region-coherence fix is untouched.

## still open (not fixed here, and NOT this item's fix to make)

**Canyon seeds (1, 3, 4, 8) still read as nearly the same NE-SW diagonal.**
Traced to root cause, not just re-observed: `mapgen_v0.py`'s `plan()`
picks `orientation_deg` for linear landforms (Canyon included) as a biome-
level "wind grain" constant plus `rng.uniform(-15, 15)` -- see
`_wind_grain(field9)` at `mapgen_v0.py:459`. All 8 plans read the SAME
`deep_desert.md` sheet, so all four Canyon seeds draw from the same grain
+/-15 degrees, landing at 48/56/56/67 degrees -- a chooser-level decision,
not a painter one. `mapgen_paint.py`'s own `_organic_channel` already
gives each seed a distinct wander/notch pattern (confirmed: each canyon's
detailed path differs), but a painter cannot make four channels pointing
within 20 degrees of each other read as differently-oriented at thumbnail
scale. This is `MACRO_GENERATOR_V0_1`'s chooser code, out of
MAPGEN_PAINTER_V1_1's own docstring scope ("never chooses a landform...
untouched by this item"); flagging there, not fixing here.

## grade (thumbnail-scale honesty, per the item's EXPECT/LIES; FOUNDRY, no
owner review yet -- this is not a keep/cut, it stands until he looks)

Net read: unchanged from round 2's coherent-region composition, plus the
brine_seep canyons (1, 3, 8) now show a small but genuinely visible green
patch beside the channel -- "has hydrology" and "no hydrology" (seed 7,
Crater, none) are now distinguishable by eye on the sheet, which they were
not before. The canyon-orientation sameness remains the honest open item,
and it is a chooser fix, not a round-4 painter target.
