# CORPUS_MAP_STATISTICS_1 — topology statistics over the 44 hand-authored maps, plus vanilla controls

Spec source: `design/RimMandrake/map_content_injection_research.md` §9.3 step 3
(owner ruled 2026-09-06: *calibration and regression are fine; never acceptance*).
These numbers TUNE the generator's parameters and CATCH drift. They never say a
map is good — the owner's eye on a comparator sheet is the only acceptance.
⛔ Do not build a "distance to nearest corpus map" scorer; the owner rejected it.

## spec

- Input: the 44 `.rws` under `research/RimMandrake/hand_authored_maps/` via
  `savemap.py` (terrain grid as shortHashes — NO def-name resolution needed for
  topology; corpus mod sets differ from ours, `beautiful_tilemap.md` §6a).
- Controls: ≥10 vanilla-generated maps at matched sizes (250², 275², 300²) and
  arid biomes, captured from quicktests via the bridge terrain read (one bridge
  session; or from any existing vanilla saves on disk if size-matched).
- Features, per map, all hash-only:
  - connected-region size distribution (count, mean, p50, p90, max fraction)
  - perimeter/area per region (edge complexity), overall and for the largest 5
  - openness: fraction of cells whose terrain family is passable, global and in
    25×25 windows (distribution)
  - terrain-pair adjacency matrix as structure (how many distinct pairs, entropy),
    not as named pairs
  - chokepoints: count and min width of cuts between the two largest open regions
    (approximation is fine; say which)
  - distinct-terrain count (already known: 11-44, median 19)
- Stratify by size and by game version (1.4 ×21, 1.5 ×16, 1.6 ×7) — a statistic
  that merely detects "is 500²" or "is 1.4" measures nothing (`beautiful_tilemap.md`
  §6b). Report which features separate corpus from controls AFTER stratification,
  and which do not.
- Output: one CSV (map, size, version, biome-if-known, features…), one short
  markdown summary in `research/RimMandrake/reference/` naming the features that
  separate and their corpus ranges (these become the generator's calibration
  targets and the regression band), and the script in `rimbench/` with a
  selftest on one synthetic grid with known region counts.

## verify

The summary states, per feature, the corpus range and whether it separates from
controls after stratification. A known-answer check: a synthetic grid with 3
regions of known sizes reports exactly those. Zero rows for any of the 44 is a
failure, not a footnote.

## not chasing

Semantics (is it water, is it buildable — needs def names), the things layer,
any learned model, any single "score."
