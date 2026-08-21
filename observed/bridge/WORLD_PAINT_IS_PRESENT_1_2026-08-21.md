# WORLD_PAINT_IS_PRESENT_1 — run 1, live, full-583

Game UP, world `Ash'karr` seed `grasshopper`, 21,872 tiles. Bridge held by CHECK.

## RESULT: PASS. The paint is present. The world was one CSV generation behind, and it is now level.

⛔ **The spec's own three signatures would have called this a bare regeneration, and they
would have been wrong.** `AB_OcularForest` read **0**, not 3. `rain_mm 0` read **0 rows**,
not 20,113. On those two tells alone the correct action was "say so loudly before anyone
builds on this save". The tells were right about the fact and wrong about the cause.

## The instrument
⛔ Not a grep, and not the biome histogram either — a histogram agrees on a total while
disagreeing tile by tile. **`jawa/world_tile_validate`**, which compares the live world to
the CSV row by row and *"reads RAW tile fields, never the cached properties"*.

    rows 21872 · matched 1756 · mismatched 20116 · matchPct 8.03%
    byField: { rainfall: 20113, elevation: 312, biome: 3 }

## The difference, named — three fields, and each is one commit

| field | tiles | live | CSV | the commit that made the CSV differ |
|---|---|---|---|---|
| rainfall | 20,113 | 18–90 | 0 | `a672c8f` 09:03 *Rain stops falling on the Dune Sea…* |
| elevation | 312 | +1411 | −30 | `bd5dad0` 08:34 *The Scald was a lake perched 1,300 m above its own shoreline* |
| biome | 3 | ExtremeDesert | AB_OcularForest | `bdb78ff` 08:59 *AB_OcularForest was painted on zero tiles…* |

**Nothing else on 21,872 tiles differed at all** — not temperature, not hilliness, not
swampiness, and not the other 24 biomes, which matched to the tile:
`AB_RockyCrags 4440`, `ExtremeDesert 3578(+3)`, `AridShrubland 2401`, `Desert 2147`,
`Ocean 1468`, `Lake 312`, `ZBiome_Grasslands 233`, `AB_PyroclasticConflagration 31` …

🔑 **That is the shape of a STALE world, not a bare one.** A regeneration disagrees
everywhere, across every field. This disagreed on exactly three hand edits and nowhere
else. The chronology closes it: the last world save is `WORLDMAP_gen2.rws` at **08:25**;
all three CSV commits land at **08:34, 08:59 and 09:03** — after it. The world did not
lose the paint. The paint moved on without the world.

## The round trip, proven end to end
Because this world is scratch (owner, 2026-08-21: *"use the world for testing purposes"*):

    jawa/world_tile_import  path=…ASHKARR_WORLDMAP_tiles.csv apply=true expectTiles=21872
      -> applied 21872, skipped 0, errors [], unknownBiomes []
    jawa/world_commit       -> failedSteps 0
    jawa/world_tile_validate
      -> rows 21872 · matched 21872 · mismatched 0 · matchPct 100.0 · byField {}

**21,872 of 21,872, raw fields, zero mismatches.** The whole planet reaches a running game
over the bridge in three calls and about a second of engine time. That is worth more than
the diff was: the import path is no longer a hope.

⭐ `unknownBiomes: []` also retires a live question — **`AB_OcularForest` is a real loaded
BiomeDef on this stack.** It was absent from the world because the world predated the
commit that painted it, not because the def failed to load.

## Side effect, deliberate and reported
`jawa/world_stats` moved **6.71% → 8.14% water, 2 bodies → 3**, matching the bundle
exactly. See THE_SCALD_LOST_ITS_WATER_1: sinking the Scald to −30 is what did it.
