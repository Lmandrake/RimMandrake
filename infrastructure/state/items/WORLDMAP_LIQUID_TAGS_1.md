# WORLDMAP_LIQUID_TAGS_1 — typed liquid bodies on the frozen world drive landing mapgen

Filed by BENCH, 2026-09-13 (owner ruling: typed tiles drive mapgen —
`design/RimMandrake/liquids_framework_design.md` §4 "Typed worldmap → mapgen").

## spec

Two halves. (1) AUTHORING: one bridge pass writes `worldTag` liquid types
onto the frozen Ash'karr map's water tiles and named bodies — building ON
`LIQUID_BIOMES_MAP_1`'s four authored bodies (boiling ocean, two brine seas,
propane lake) plus the ordinary seas/lakes; stored in a WorldComponent keyed
by tile ID. No worldgen, no re-render. (2) MAPGEN: a GenStep reads the landing
tile's tag and REPAINTS the vanilla-generated shores/lakes to that row's
terrain suite — paint-over of generated terrain, untyped tiles untouched.

## verify

Bridge-read the tags back after the authoring commit (`world_commit` — no
commit, no edit). Land a quicktest colony on a tagged tile: shores read the
row's TerrainDefs via `get_terrain`; land on an untyped tile: byte-identical
vanilla behavior. Save nothing over the canonical start save.

## Watch out

- 🔴 The world is frozen and hand-authored — live bridge WRITES are an
  opus-tier act (Agent_Policy forbidden-list #2); one bridge driver at a time;
  back up before the pass and verify what you displaced, not just what you
  wrote.
- The 100-row cap on every bridge world read — page, never trust one read.
- Depends on LIQUID_REGISTRY_CORE_1 for the rows the tags name.
- model: opus (frozen-world writes + mapgen Harmony/GenStep C#).
