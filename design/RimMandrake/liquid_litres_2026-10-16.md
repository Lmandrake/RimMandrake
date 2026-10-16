# Liquids count in litres — LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (2026-10-16)

Owner, 2026-10-16, after watching colonists drain a pond by filling barrels, buckets and bottles:
*"We ruled on the water tank capacity. A barrel should not be able to hold the same as a 1x1 solid tank. Do some basic
volume calculations..."* Then by card: *"Count in Litres, and also show meters of depth when hovering over liquid (or tell
me that's not possible)"*.

The standing ruling it builds on (2026-10-12, `natural_bodies_as_canals_design_2026-10-11.md` §8): one tank square = one
deep pond square = one deep canal square = 4 levels (`RM_Volume.LevelsPerSquare`). That is unchanged.

## The computation (owner accepted the method)

- A vanilla human draws 1.20 cells tall (MEASURED 2026-10-16) and is about 1.75 m, so **1 cell ≈ 1.46 m**.
- Deep water is about 2 m (ASSUMPTION), and deep is 4 levels, so **1 level ≈ 0.5 m**.
- One deep square ≈ 1.46² × 2 ≈ **4.26 m³ ≈ 4,300 L**; one level ≈ 1.07 m³.
- The old tank unit was a fifth of a level: ≈ 213 L, a 55-gallon drum. Old containers held barrel 25 units, bucket 5,
  bottle 1 — about 5,300 L, 1,070 L and 213 L. Against real sizes (barrel 208 L, bucket 15 L, bottle 1.5 L) that is
  25×, 70× and 140× too big.

## Constants chosen (`Source/RM_Volume.cs`)

| constant | value | why |
|---|---|---|
| `LitresPerLevel` | **1,000** (1 m³) | within 7 % of the computed 1,066 L. The 2 m depth assumption carries more error than that. A round number makes every readout legible: a level is 1 kL and a deep square is 4 kL. It implies a cell of √2 ≈ 1.41 m, 3 % under the measured 1.46 m. |
| `MetresPerLevel` | 0.5 | deep (4 levels) = 2 m |
| `LevelsPerSquare` | 4 | unchanged (ruling 2026-10-12) |
| `UnitsPerLitre` | 10 | **the integer tank unit is a decilitre** |
| `UnitsPerLevel` | 10,000 | `LitresPerLevel × UnitsPerLitre` |
| `UnitsPerSquare` | 40,000 (4 kL) | |
| `LegacyUnitsPerLevel` / `LegacyUnitLitres` / `LegacyUnitScale` | 5 / 200 L / 2,000 | one model-2 unit, for migration |
| `CurrentModel` | 3 | 1 = before POND_VOLUME_UNIFY, 2 = 5 units a level, 3 = litres |

**Integer decilitres, not float litres.** Every ledger outside the flow kernel (tanks, hoses, pumps, nets, settle,
converters, the transfer service) is integer and conservation-tested on exact integers. A 1.5 L bottle needs sub-litre
resolution. Decilitres keep all of it integer and exact (bottle 15, bucket 150, barrel 2,080). Players only ever see
litres: `RM_Volume.FormatLitres` / `FormatUnits` give "1.5 L", "208 L", "4 kL", "12.5 kL". The int range is ample: a
64 kL extra-tall tank is 640,000 units.

**The kernel stays in integer levels.** Canal and pit cells hold whole levels (`fillGrid`). Ponds keep their float stock
in fill-units of levels (`volumePerTile` per level). Neither changed. The conversion is at the boundary: a level is
`RM_Volume.UnitsPerLevel` tank units, so a pump moves 1,000 L per level.

## Containers (owner's sizes)

| container | before | now | material `capacityFactor` |
|---|---|---|---|
| bottle | 1 unit (≈213 L) | **1.5 L** (15 units) | still multiplies (leather/glass/metal…), rounded to 0.1 L |
| bucket | 5 units (≈1,070 L) | **15 L** (150) | wood/metal/leather |
| barrel | 25 units (≈5,300 L) | **208 L** (2,080), a 55-gal drum | wood/metal/plasteel |

- `LiquidBottledForm.litresPerBottle / litresPerBucket / litresPerBarrel` (floats, litres) replace `unitsPer*`.
  `generate_liquid_suite.py` emits them from `CONTAINER_LITRES`; the registry XML is generated.
- **A pond loses only the litres taken.** `RM_LiquidBottleUtility.TryDebitTerrain` debits
  `units × volumePerTile ÷ UnitsPerLevel` fill-units. A bottle is 0.0015 of a level. A barrel is about a twentieth of a
  deep square.
- Bottles do not fill from canals: canal fill terrains are not in any LiquidDef's terrain suite. That was true before
  and is unchanged. A pump drawing a canal level yields 1,000 L into tanks.
- **The adopted item forms keep the old unit's size, 200 L: the vanilla Chemfuel item and VGE astrofuel.** This leaves
  the fuel economy unchanged: tar refines 4:1 into Chemfuel items, and the VE pipe adapter's 1 item per 200 L. The
  owner may want a smaller item. **OWNER CALL.**

## Every place a unit is used

| system | change |
|---|---|
| tanks (`Building_LiquidTank`) | capacity via `RM_Volume.TankCapacity` (2×2 = 16 kL, tall/cargo 32 kL, extra-tall 64 kL); inspect "Holding: Water (8 kL / 16 kL)"; save migration |
| cargo tank, tank styles | same constant (footprint × UnitsPerSquare × height) |
| ponds (capacity, stock, refill, recession) | unchanged: fill-units of levels. Inspect `StockReport` and the level holder now say litres. |
| canal fill levels, pits | unchanged integer levels; mouseover shows depth and litres |
| pumps (per pulse) | `TankUnitsPerLevel` = 10,000 → 1 kL per level; `PourLevels` against the dump rate in units |
| hoses | `hoseLitresPerCell` **5 L** (setting; a ~65 mm hose 1.46 m long holds 4.8 L). The old 0.2 units was 40 L a cell. A hose is a container, so it gets a real size. `heldUnits` migrated. |
| tank-to-tank settle, Dump drain | `tankLitresPerCycle` 2,000 L, `dumpLitresPerCycle` 1,000 L (= the old 10 and 5 units) |
| spills / filth | `litresPerFilth` 400 L (= old 2 units) |
| containers, bottles / drink / wash | litres above; drinking and washing consume whole items (no units) |
| converters / stills / works (`CompLiquidConverter`, `LiquidConversion`) | `inputLitresPerDay`, `distillInputLitres`/`distillOutputLitres`, `inputLitres`/`outputLitres`/`productCount`. **Every number is the old value × 200 L**, so rates and ratios are unchanged (a solar still at 6,000 L/day). **OWNER CALL** if machines should get real-world rates too. |
| reaction vat (`RM_LiquidReactionDef`) | `litresA`/`litresB`/`productLitres`/`productCount` (×200 L) |
| liquid bath recipes | `litresPerCraft` 1,000 L (= old 5 units) |
| VE pipe adapters | `litresPerRareTick` 2,000, `resourcePerLitre` 0.005 (1 VE item per 200 L, as before) |
| ruins' starting stock | at least one level |
| map controls (Source / Sink / Level holder) | count levels (unchanged); inspect adds litres; `RateLabel` says a level is 1 kL |
| subsurface drill reserve | fill-units of levels (unchanged); report in litres |
| liquid heat, fire burn | levels (unchanged) |
| Dubs Bad Hygiene bridge | terrain tags and drinkable items only, no units (unchanged) |
| ExplosiveGrowth irrigation | no FlowWorks unit use found (`grep` 2026-10-16) |
| other mods | Cauldron gas tap: one banked unit = 200 L into tanks via `RM_Volume.Units`. LuminousPigment GlowTank: one draw = 200 L, read by reflection off `RM_Volume.Units(float)`. WreckedMachines distillation module XML in litres. |
| mod settings text | tank slider says kL; pump text says a level is 1,000 L (a cubic metre) |

## Save migration (model 2 → 3, once)

- Every holder of tank units saves `rmVolumeModel`. If it is absent, the holder was saved under model 2. On
  `LoadingVars` it converts with `RM_Volume.FromLegacyUnits` (×2,000, clamped) and marks itself 3. The holders are tanks
  (`storedUnits`), hose reels (`heldUnits`), converters (`accrued`, `totalIn`, `totalOut`) and pipe adapters
  (`moved`). The marker is per object, so a tank that is minified, in a caravan or on another map converts on its own
  load, in any order.
- `RM_MapComponent_Excavation`'s `RM_volumeModel` goes to 3 with a log line. Ponds are rescaled only from model 1;
  2 → 3 changes no pond.
- The mod settings file stores the four renamed settings under new keys. The old keys are read once, ×200 L. An
  untouched old hose default (0.2) becomes the new 5 L, not 40 L.
- Selftests: `Volume_litres_model_3` (constants, conversion, clamping, mutation probe, formats, readout, bottle debit)
  and `Volume_litres_production_wiring` (each holder's marker and conversion, the settings readers, the mouseover patch).

## Mouseover depth — possible, and built

The bottom-left cell readout is `Verse.MouseoverReadout.MouseoverReadoutOnGUI`. It caches the terrain line per
`TerrainDef` (`cachedTerrain` / `cachedPolluted` / `cachedTerrainString`), so a per-square number cannot ride on the
terrain label. `RM_Patch_MouseoverDepth` (Harmony prefix) writes the line itself on a liquid square: vanilla's own parts
plus "— 1.5 m deep, 3 kL". It then sets the cache keys so vanilla prints the line unchanged. On a dry square it clears
the cache once, so vanilla rebuilds its own line.

- Dug canals and pits read their fill levels.
- Natural water reads its bed depth (`BedLevelsAt`), scaled by the pond's fill when the pond is limited.
- The setting `mouseoverDepthEnabled` (on) switches it off.

Not yet seen live.
