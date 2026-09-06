# comparator_sheet.png -- caption legend

`render_terrain.py --sheet` captions are filenames only; premises here.

Deep desert (`deep_desert.md`), 250x250, seeds 1-8:

1. seed01.grid.txt -- Canyon -- "A canyon shapes the whole map, anchored on the head."
2. seed02.grid.txt -- LoneMountain -- "A lone rock shapes the whole map, anchored on the lee foot."
3. seed03.grid.txt -- Canyon -- "A canyon dominates the map; the only way through is at the narrows."
4. seed04.grid.txt -- Canyon -- "A canyon dominates the map; the only way through is at the head."
5. seed05.grid.txt -- Sinkhole -- "One sinkhole cuts the ground, and everything answers to the pit floor."
6. seed06.grid.txt -- Sinkhole -- "A sinkhole dominates the map; the only way through is at the lip."
7. seed07.grid.txt -- Crater -- "A crater dominates the map; the only way through is at the ring centre."
8. seed08.grid.txt -- Canyon -- "A canyon shapes the whole map, anchored on the head."

Corpus crops (arid, whole-map -- render_terrain.py has no .rws cropping,
so these render whole, not cropped, as the item's fallback allows):

- InMemoryOfRain.rws (325x325) -- Desert, "a river fans into a dry delta"
- DesertedTrader.rws (275x275) -- Desert, "one rock in a wide gap"
- LushRiverRelease.rws (250x250) -- AridShrubland, "a river runs the valley floor"
- PointSea.rws (275x275) -- AridShrubland, "a headland pushes into the sea"
- BloodGulch - Exits.rws (250x250) -- AridShrubland, "one red gulch cuts the shrubland corner to corner"
