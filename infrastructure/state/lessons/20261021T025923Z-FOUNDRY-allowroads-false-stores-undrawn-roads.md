SurfaceTile.Roads is null when the biome has allowRoads=false, so record road links on that biome are stored but never drawn (196 on Stillsand, 34 on Umbra). Check a drawn-road count against allowRoads, not link counts.
home: skills/rimworld-world-editing
