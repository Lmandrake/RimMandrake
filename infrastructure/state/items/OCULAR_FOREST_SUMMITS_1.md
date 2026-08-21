## spec
`AB_OcularForest` is painted on **0 tiles**. Its gate in
`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §6 read `>2350 m` and the map's
highest tile is **2266 m**, so it could never have been placed. The owner reset the gate to
`> 2000 m` on 2026-08-21.

In `world/ASHKARR_WORLDMAP_tiles.csv`, set `biome` to `AB_OcularForest` on exactly three
rows:

| tile | elev_m | region | currently |
|---|---|---|---|
| `4299` | 2190 | The Ashfall Range | `ExtremeDesert` |
| `9158` | 2177 | The Ashfall Range | `ExtremeDesert` |
| `9159` | 2117 | The Ashfall Range | `ExtremeDesert` |

These are the **highest non-volcanic ground on the planet** and they are adjacent — "tiny
patches" on the summits, which is what the entry always described.

⛔ **Do not paint the other eleven tiles above 2000 m.** Nine are the planet's one volcanic
province (`Volcano` · `LavaField` · `AB_PyroclasticConflagration`) and §6 says there is
exactly one such province. ⛔ **In particular do not take `11961`, `11965` or `7101`** — they
are the only high tiles carrying river flow, which makes them the tempting choice, and all
three are `Volcano`.

⚠️ **`AB_OcularForest` must survive the biome cut and be loadable.** Confirm it resolves
before painting; a biome defName that does not load leaves three tiles pointing at nothing.

## verify
- `AB_OcularForest` tile count in `world/ASHKARR_WORLDMAP_tiles.csv` is **3**, not 0
- the distinct-biome count goes **24 → 25**, and §6's "24 distinct biomes are painted"
  sentence is updated with it
- no tile whose biome is `Volcano`, `LavaField` or `AB_PyroclasticConflagration` changed

## criteria
The world map shows a red-streaked patch on the Ashfall Range summits and nowhere else.
