# MAPGEN_PAINTER_V1_1 — make the offline terrain painter draw like a landscape, not a diagram

Owner 2026-09-06 (research doc §8 #9): improve the painter until it converges with what GL draws. The v0 sheet (`Transient/mapgen_v0/comparator_sheet.png`) failed the eye: a straight band with rounded ends for a canyon, perfect circles for crater/sinkhole/mountain, hard edges, 4-6 terrains vs the corpus's 13-24, no hydrology.

## spec (in `src/RimMandrake/Utils/rimbench/mapgen_v0.py`'s `grid()`, or a `mapgen_paint.py` it calls)

1. **Organic masks.** Every primitive mask is domain-warped by `fbm` (two noise fields offsetting x/z) before thresholding; a canyon is a `walk` with wander ≥0.35, variable width, side notches (`blob`s along it), not a rounded rectangle; a crater/sinkhole rim is a `rim_band` broken by `clumps`; a lone mountain is a `blob` with roughness ≥0.45 plus a talus apron. Composition rule 1: boundaries jagged and staggered, never straight, never a perfect circle.
2. **Elevation → terrain bands.** Build a scalar height field (landform mask + fbm), then map height to terraced terrain: rock (impassable, Granite/Sandstone `_Rough`) → `RoughHewn` → `Gravel` → `Sand`/`SoftSand`, plus `PackedDirt`/`Soil` on the lee side. Target the corpus's distinct-terrain count (13-24) and perimeter/area (2.6-3.1) from `corpus_map_stats.md`, measured by running `corpus_stats.py`'s functions on the generated grid (import them; do not duplicate).
3. **Hydrology with a cause.** When the plan has hydrology, draw it: a dry riverbed (`walk`, wide, `Gravel`/`Mud` floor) from the landform's high side to the map edge, a delta fan if the plan says so, `WaterShallow` only where the cause justifies it. Rule 3.
4. **Gates stay honest.** Impassable rock now exists, so connectivity/buildable-area can FAIL — that is the point; report the failures rather than avoiding rock.
5. Re-render the 8 v0 plans; `render_terrain.py --sheet` them beside the same 5 corpus maps → `Transient/mapgen_v1/comparator_sheet.png`. Selftest extends v0's: every generated grid has ≥10 distinct terrains and perimeter/area within 2.4-3.3.

## verify

```
PROVE   the v1 sheet exists; corpus_stats on the 8 grids reports distinct_terrains ≥10 and perimeter/area in band for ≥6 of 8; the owner marks keep/cut
EXPECT  at thumbnail size a v1 canyon is mistakable for Blood Gulch's gulch in kind (wandering, notched), not for a road
LIES    statistics inside the corpus band on a map that still reads as a diagram — the sheet is the acceptance, the numbers are the regression gate
```

## not chasing

GL fidelity (that is MAPGEN_CONVERGENCE_LOOP_1's comparison); structures; plants beyond terrain.
