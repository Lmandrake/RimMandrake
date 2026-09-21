# GRASSLANDS_TILES_CSV_STALE_1 — `world/ASHKARR_WORLDMAP_tiles.csv` may be stale vs. the live game for Grasslands/Pyrelands

## Found incidentally while closing `BIOME_CAST_PATCH_DEAD_NAMES_1`, 2026-09-20 FOUNDRY

Re-checking `world/ASHKARR_WORLDMAP_tiles.csv` for a different question (whether
`gen_cast_patch.py`'s new refusal guard should fire), found:

    ZBiome_Grasslands tiles: 222
    RM_FE_Pyrelands tiles:   0

**That is the exact reverse of the closed item `GRASSLANDS_CAST_DEAD_BIOME_1`'s own
measurement**, which reads: *"That biome [`ZBiome_Grasslands`] carries ZERO tiles on
the frozen world — MEASURED at `f7e2bd21c` via `jawa/world_tile_export` over all
21872 surface tiles, against 222 `RM_FE_Pyrelands` tiles."*

`f7e2bd21c` (2026-09-18 22:08, commit title itself: *"Pyrelands wiring pointed at a
biome with ZERO tiles"*) is dated AFTER the newest commit that actually touches
`world/ASHKARR_WORLDMAP_tiles.csv` in this repo — `1df76373c`
(`WORLD_NAME_FIXES_1`, 2026-09-12 20:47). `f7e2bd21c`'s own measurement instrument
was `jawa/world_tile_export`, i.e. a LIVE bridge read of the running game, not this
CSV — and nothing in this repo re-exported that live state back into the CSV
afterward.

## Two readings, not adjudicated here

1. **The CSV is simply stale** — the Pyrelands world-switch that `f7e2bd21c` measured
   live never got written back to `world/ASHKARR_WORLDMAP_tiles.csv`, so the
   "frozen, one CSV" canonical file (per CLAUDE.md's Ash'karr map doctrine) currently
   disagrees with the actual game world by 222 tiles' worth of biome identity.
2. **The live game has since reverted** — something after `f7e2bd21c` repainted those
   222 tiles from `RM_FE_Pyrelands` back to `ZBiome_Grasslands` live, and the CSV
   (last touched 2026-09-12, i.e. BEFORE `f7e2bd21c`) was never wrong to begin with —
   it's the live state that moved.

Not distinguished in this pass — that needs a fresh live `jawa/world_tile_export` and
a diff against the CSV, and the game must stay up and untouched per this pass's own
constraints (bridge not to be driven for an unrelated task).

## Why this matters beyond bookkeeping

`GRASSLANDS_CAST_DEAD_BIOME_1` closed on the strength of that RM_FE_Pyrelands
measurement — its cast animals (`RSW_Zeer`, `RSW_Nuna`, `RSW_Gizka`, `RSW_Orray`,
`RUT_Emberscythe`, `AA_FireWasp`) were retargeted INTO `RM_FE_Pyrelands`'s own
`wildAnimals` on the premise that biome is what's actually painted. If `ZBiome_
Grasslands` (a donor biome, never owned, never fitted with the owner's Pyrelands
ecology) is what 222 tiles actually carry today, those six animals may currently be
cast into a biome nobody plays on, and whatever donor `ZBiome_Grasslands` ships by
default (unknown, unaudited) is what those 222 tiles' wild spawns actually use.

## Not touched this pass

Out of scope for `BIOME_CAST_PATCH_DEAD_NAMES_1`, and the game is up under
constraints that forbid driving the bridge for this task. Whoever picks this up:
`jawa/world_tile_export` (fresh, live) is the instrument, not another CSV read.

## verify

A fresh live `jawa/world_tile_export` for the 222 tiles in question, diffed against
`world/ASHKARR_WORLDMAP_tiles.csv`'s `biome` column for the same tile IDs, settles
which of the two readings above is true.
