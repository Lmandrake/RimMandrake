# CORPUS_STATS_VANILLA_CONTROLS_1 — the control population for corpus_stats.py

Follow-up to `CORPUS_MAP_STATISTICS_1` (closed 2026-09-06 without controls — the corpus half is done, the comparison half is this item). `beautiful_tilemap.md` §6b: a feature that cannot separate hand-authored maps from vanilla-generated ones at matched size cannot calibrate anything.

## spec

- Capture ≥10 vanilla-generated terrain grids at matched sizes (250², 275², 300²) in arid biomes: quicktests on the minimal list, `jawa/world_tile_map_generate` at chosen tiles or repeated `start_debug_game_ready`, terrain read via the bridge terrain batch read, written in `render_terrain.py`'s text-grid format (defNames) under `research/RimMandrake/reference/controls/`. One bridge session.
- Extend `corpus_stats.py` to accept text grids (hash the defName string for the category id) and a `--controls <dir>` flag; add a "corpus vs controls" section to `corpus_map_stats.md`: per feature, both ranges and whether they overlap, stratified by size.
- Replace or drop the chokepoint proxy: at plus-erosion granularity it read 1 on all 44 maps. Either a multi-radius erosion (report the radius at which the two largest open regions disconnect) or remove the feature and say so.

## verify

```
PROVE   corpus_map_stats.md has a corpus-vs-controls section with n≥10 controls at matched sizes
EXPECT  at least one feature (perimeter/area or openness-std are the candidates) shows non-overlapping p50 bands; chokepoint no longer constant
LIES    controls generated at a different size or biome than the corpus rows they are compared to — a size-driven feature then reads as a corpus/vanilla difference
```
