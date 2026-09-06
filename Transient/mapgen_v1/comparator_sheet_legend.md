# comparator_sheet.png (v1) -- caption legend

MAPGEN_PAINTER_V1_1. Same 8 plans (same sheet, same seeds) as
`Transient/mapgen_v0/comparator_sheet.png`, repainted by `mapgen_paint.py`
instead of v0's straight-band/perfect-circle carving; same 5 corpus crops
for a like-for-like comparison. `render_terrain.py --sheet` captions are
filenames only; premises here.

Deep desert (`deep_desert.md`), 250x250, seeds 1-8:

1. seed01.grid.txt -- Canyon -- "A canyon shapes the whole map, anchored on the head."
2. seed02.grid.txt -- LoneMountain -- "A lone rock shapes the whole map, anchored on the lee foot."
3. seed03.grid.txt -- Canyon -- "A canyon dominates the map; the only way through is at the narrows."
4. seed04.grid.txt -- Canyon -- "A canyon dominates the map; the only way through is at the head."
5. seed05.grid.txt -- Sinkhole -- "One sinkhole cuts the ground, and everything answers to the pit floor."
6. seed06.grid.txt -- Sinkhole -- "A sinkhole dominates the map; the only way through is at the lip."
7. seed07.grid.txt -- Crater -- "A crater dominates the map; the only way through is at the ring centre."
8. seed08.grid.txt -- Canyon -- "A canyon shapes the whole map, anchored on the head."

Corpus crops (arid, whole-map -- unchanged from the v0 sheet):

- InMemoryOfRain.rws (325x325) -- Desert, "a river fans into a dry delta"
- DesertedTrader.rws (275x275) -- Desert, "one rock in a wide gap"
- LushRiverRelease.rws (250x250) -- AridShrubland, "a river runs the valley floor"
- PointSea.rws (275x275) -- AridShrubland, "a headland pushes into the sea"
- BloodGulch - Exits.rws (250x250) -- AridShrubland, "one red gulch cuts the shrubland corner to corner"

## grade (thumbnail-scale honesty, per the item's EXPECT/LIES)

1. seed01 Canyon -- **yes**: wandering diagonal channel, wall width visibly
   varies, a wide notched head chamber, no straight edges.
2. seed02 LoneMountain -- **partly**: silhouette and talus apron are
   properly irregular, but the interior rock/RoughHewn terrace still nests
   as visible near-concentric rings (a soft bullseye) at closer-than-thumbnail
   zoom.
3. seed03 Canyon -- **yes**: same wandering-channel family as #1, a wide
   head chamber with a rock-alt intrusion, notch bulges along the wall.
4. seed04 Canyon -- **yes**: consistent with #1/#3, corner-to-corner
   diagonal in the Blood Gulch idiom, no rounded-rectangle read.
5. seed05 Sinkhole -- **yes**: rim is broken and irregular (not a ring),
   an organic Marsh floor patch, plus a real spur channel reading as a
   dry wash leading off the bowl.
6. seed06 Sinkhole -- **yes**: cleanest of the radial set after shrinking
   the lee-deposit patch -- broken rim, amoeba-shaped Marsh floor, no
   stray circle competing with it.
7. seed07 Crater -- **yes**: broken double rim, mottled floor; the
   lee-deposit fleck on the rim reads as weathering, not a second feature.
8. seed08 Canyon -- **yes**: same family as #1/#3/#4.

Net: 7/8 yes, 1/8 partly (LoneMountain's internal terrace rings). None of
the 8 reads as a straight band or a perfect circle any more; that was
100% of the v0 sheet's failure mode.
