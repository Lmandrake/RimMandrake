# comparator_sheet.png (v2) -- caption legend

MAPGEN_PAINTER_V1_1 round 2. Same 8 plans, same sheet/seeds as v0 and v1
(`Transient/mapgen_v0/`, `Transient/mapgen_v1/`); repainted by the fixed
`mapgen_paint.py` (boundary-only terrace jitter + a post-paint boundary
roughening pass, see that file's `_terrace_paint`/`_roughen_boundaries`
docstrings for the mechanism and the corpus_stats.py sweep that picked
strength=0.25). Same 5 corpus crops as v1, for a like-for-like comparison.

Deep desert (`deep_desert.md`), 250x250, seeds 1-8 -- same premises as v1
(landform choice/premise text is mapgen_v0.py's plan(), untouched here):

1. seed01.grid.txt -- Canyon
2. seed02.grid.txt -- LoneMountain
3. seed03.grid.txt -- Canyon
4. seed04.grid.txt -- Canyon
5. seed05.grid.txt -- Sinkhole
6. seed06.grid.txt -- Sinkhole
7. seed07.grid.txt -- Crater
8. seed08.grid.txt -- Canyon

Corpus crops (unchanged from v0/v1): InMemoryOfRain.rws, DesertedTrader.rws,
LushRiverRelease.rws, PointSea.rws, BloodGulch - Exits.rws.

## measured (corpus_stats.py, 250-bucket band from corpus_map_stats.md)

|              | v1 (round 1) | v2 (round 2) | corpus 250-bucket band |
|---|---|---|---|
| region_size_max_frac | 0.036-0.100 | 0.065-0.285 | 0.044-0.635 |
| region_count | 2896-3613 | 128-547 | 496-3056 |
| perim_area_mean | 2.640-2.686 | 2.632-2.893 | 2.619-3.064 |

v1's in-band perim_area was an artefact of fragmentation (many tiny jagged
regions raise total perimeter per area on their own); v2 gets a genuinely
coherent region structure AND an in-band perimeter/area at the same time --
see mapgen_paint.py's `_roughen_boundaries` docstring for the two-step
finding (fixing max_frac first regressed perim_area below band; a second,
narrowly-targeted boundary-roughening pass recovered it without
re-fragmenting the interior).

## grade (thumbnail-scale honesty, per the item's EXPECT/LIES; FOUNDRY, no
owner review yet -- this is not a keep/cut, it stands until he looks)

Net read: the whole sheet now composes like the corpus panels do -- a few
big, readable ground/relief regions plus texture, not "one feature on
noise". The v1 problem (uniform speckle, no large coherent regions) reads
as fixed by eye, not just by the numbers above.

1. seed01 Canyon -- coherent diagonal channel, wide bed, broken banks;
   background reads as a few big patches, not static.
2. seed02 LoneMountain -- clear rock core with a mottled talus apron; still
   the roundest silhouette of the 8 (mountain's own mask has the least
   directional bias of any category here).
3-4, 8. Canyon variants -- same family as #1, distinct wander per seed.
5-6. Sinkhole -- broken rim visible, floor reads as its own region, not a
   ring artefact.
7. Crater -- double rim survives, floor is one coherent patch.

Open item for round 3: all four Canyon seeds (1, 3, 4, 8) still read as
nearly the same diagonal at thumbnail scale -- `orientation_deg` is varying
per plan but the channel's own shape doesn't visibly diverge from it; and
the point hydrology (brine_seep/spring dressing) is too small a patch to
read at all at this scale, so "no hydrology" and "has hydrology" look
identical on the sheet. Both are chooser/painter-parameter questions, not
the region-coherence problem this round targeted.
