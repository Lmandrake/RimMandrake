## spec
Ruling, mechanism and the owner's answer: `items/D-V2-RAIN.md`. This item is one column
edit in `world/ASHKARR_WORLDMAP_tiles.csv`.

```
rain_mm = 0  WHERE  NOT (
                     ( hilliness >= 4 AND biome NOT IN {Volcano, LavaField,
                       AB_PyroclasticConflagration, Scarlands, AB_TarPits} )
                     OR biome == AB_FeraliskInfestedJungle
                   )
```

**Measured effect, 2026-08-21:**

| | tiles |
|---|---|
| rows set to 0 | **20,113** — 16,845 of them were already ≤49 mm and change nothing in feel |
| genuinely wet tiles dried (≥600 mm) | **302** |
| tiles keeping rain | **635** — 359 river jungle, 276 non-volcanic mountain |
| volcanic province tiles keeping rain | **0** |

🔑 **Why 0 and not a low number.** Every rain `WeatherDef` carries a
`commonalityRainfallFactor` curve whose first point is `(0, 0)`, evaluated **per tile** on
`Tile.rainfall` (`WeatherDecider.cs:191`). At 0 the commonality is multiplied by **exactly
zero** and the weather can never be selected. At the current 18 mm it is a 98.6%
suppression — *rare*, not banned — and `WeatherDecider.cs:185` multiplies rain commonality
by **15** during a large fire, surfacing the residue exactly when the player is watching.

⛔ **Do not patch any biome's `baseWeatherCommonalities`.** The tile column is the whole
mechanism and it is per-tile, which no biome patch can be.
⛔ **Do not "fix" river flow afterwards.** `WorldGenStep_Rivers.cs:131` sums rainfall into
flow, but that is worldgen only and our `river_flow` column is authored and stamped.
⛔ **The volcanic exclusion is deliberate and is the owner's intent, not an embellishment.**
Without it every tile of the volcanic province keeps 1668 mm, because the province is
entirely `hilliness` 4–5 and the mountain exemption would protect it.

⚠️ **Zeroing rainfall also removes SNOW**, and that is wanted. `SnowGentle`/`SnowHard` carry
`rainRate 1` and the same curve shape, and `Desert` and `AridShrubland` currently list them
at commonality **4** — twice their `Rain`.
✅ **No painted biome is left with nothing to do.** Checked all 24: the driest still hold a
non-rain entry — `AB_RockyCrags` keeps `AB_ForsakenNight:20`, `PoisonForest` keeps
`PoisonForestSpores:18`, `BMT_FungalForest` keeps `BMT_FungalCavern:100`, `AB_PropaneLakes`
keeps `Clear:12`.

## verify
- **zero** rows where the WHERE clause above is true and `rain_mm > 0`
- `Volcano`, `LavaField` and `AB_PyroclasticConflagration` have **no** row above 0
- `AB_FeraliskInfestedJungle` still shows **271** rows at 1668 mm
- row count is unchanged at 21,872 and no column but `rain_mm` differs from HEAD

## criteria
Rain never falls on the Dune Sea, the deserts, the badlands or the volcano. It falls on the
river jungles and on the high non-volcanic ground, and nowhere else.
