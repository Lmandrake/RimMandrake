# Liquids count in litres — LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (2026-10-16)

Owner, 2026-10-16, after watching colonists drain a pond by filling barrels, buckets and bottles:
*"We ruled on the water tank capacity. A barrel should not be able to hold the same as a 1x1 solid tank. Do some basic
volume calculations..."* Then by card: *"Count in Litres, and also show meters of depth when hovering over liquid (or tell
me that's not possible)"*.

The standing ruling it builds on (2026-10-12, `natural_bodies_as_canals_design_2026-10-11.md` §8): one tank square = one
deep pond square = one deep canal square = 4 notches (`RM_Volume.LevelsPerSquare`). That is unchanged. (A notch is 0.5 m of water in one square; the word "level" is kept only for code names and for the water surface.)

## The computation (owner accepted the method)

- **A square is 2 m² of floor, 1.41 m on a side (`SquareAreaM2 = 2`). This is a definition, not a measurement.**
  A first measurement (a vanilla human draws 1.20 cells tall, about 1.75 m) gave 1.46 m a side; the 3% gap is below
  the error of the "deep water is about 2 m" assumption, so the definition stands.
- Deep water is about 2 m (ASSUMPTION), and deep is 4 notches, so **1 notch = 0.5 m** (`MetresPerLevel`).
- One deep square = 2 m² × 2 m = **4 m³ = 4,000 L**; one notch = 2 m² × 0.5 m = 1 m³ = 1,000 L.
- The old tank unit was a fifth of a notch: ≈ 213 L, a 55-gallon drum. Old containers held barrel 25 units, bucket 5,
  bottle 1 — about 5,300 L, 1,070 L and 213 L. Against real sizes (barrel 208 L, bucket 15 L, bottle 1.5 L) that is
  25×, 70× and 140× too big.

## Constants chosen (`Source/RM_Volume.cs`)

| constant | value | why |
|---|---|---|
| `LitresPerLevel` | **1,000** (1 m³) | `SquareAreaM2 × MetresPerLevel × 1000` = 2 × 0.5 × 1000. A round number makes every readout legible: a notch is 1 kL and a deep square is 4 kL. It follows from a square of 2 m² (1.41 m a side). |
| `SquareAreaM2` | 2 | one square is 2 m² of floor (1.41 m a side); by definition |
| `MetresPerLevel` | 0.5 | one notch = 0.5 m; deep (4 notches) = 2 m |
| `LevelsPerSquare` | 4 | unchanged (ruling 2026-10-12) |
| `UnitsPerLitre` | 10 | **the integer tank unit is a decilitre** |
| `UnitsPerLevel` | 10,000 | `LitresPerLevel × UnitsPerLitre` |
| `UnitsPerSquare` | 40,000 (4 kL) | |
| `LegacyUnitsPerLevel` / `LegacyUnitLitres` / `LegacyUnitScale` | 5 / 200 L / 2,000 | one model-2 unit, for migration |
| `CurrentModel` | 3 | 1 = before POND_VOLUME_UNIFY, 2 = 5 units a notch, 3 = litres |

**Integer decilitres, not float litres.** Every ledger outside the flow kernel (tanks, hoses, pumps, nets, settle,
converters, the transfer service) is integer and conservation-tested on exact integers. A 1.5 L bottle needs sub-litre
resolution. Decilitres keep all of it integer and exact (bottle 15, bucket 150, barrel 2,080). Players only ever see
litres: `RM_Volume.FormatLitres` / `FormatUnits` give "1.5 L", "208 L", "4 kL", "12.5 kL". The int range is ample: a
64 kL extra-tall tank is 640,000 units.

**Water is exactly level (owner, 2026-10-17).** Each connected body of water (pond, canal, or both joined) holds its
volume as an exact whole number of decilitres and has one surface height, worked out from that volume and the floors
under it. A square's water depth is max(0, surface - floor), computed on read. The 0.5 m notch is only the dig step and
the picture-band step. A pump moves litres, not notches. Design: `design/RimMandrake/flowworks_level_surface_2026-10-17.md`.

## Containers (owner's sizes)

| container | before | now | material `capacityFactor` |
|---|---|---|---|
| bottle | 1 unit (≈213 L) | **1.5 L** (15 units) | still multiplies (leather/glass/metal…), rounded to 0.1 L |
| bucket | 5 units (≈1,070 L) | **15 L** (150) | wood/metal/leather |
| barrel | 25 units (≈5,300 L) | **208 L** (2,080), a 55-gal drum | wood/metal/plasteel |

- `LiquidBottledForm.litresPerBottle / litresPerBucket / litresPerBarrel` (floats, litres) replace `unitsPer*`.
  `generate_liquid_suite.py` emits them from `CONTAINER_LITRES`; the registry XML is generated.
- **A pond loses only the litres taken.** `RM_LiquidBottleUtility.TryDebitTerrain` debits
  `units × volumePerTile ÷ UnitsPerLevel` fill-units. A bottle is 0.0015 of a notch. A barrel is about a twentieth of a
  deep square.
- Bottles do not fill from canals: canal fill terrains are not in any LiquidDef's terrain suite. That was true before
  and is unchanged. A pump drawing a canal notch yields 1,000 L into tanks.
- **The adopted item forms keep the old unit's size, 200 L: the vanilla Chemfuel item and VGE astrofuel.** This leaves
  the fuel economy unchanged: tar refines 4:1 into Chemfuel items, and the VE pipe adapter's 1 item per 200 L. The
  owner may want a smaller item. **OWNER CALL.**

## Every place a unit is used

| system | change |
|---|---|
| tanks (`Building_LiquidTank`) | capacity via `RM_Volume.TankCapacity` (2×2 = 16 kL, tall/cargo 32 kL, extra-tall 64 kL); inspect "Holding: Water (8 kL / 16 kL)"; save migration |
| cargo tank, tank styles | same constant (footprint × UnitsPerSquare × height) |
| ponds (capacity, stock, refill, recession) | unchanged: fill-units of notches. Inspect `StockReport` and the Level Holder now say litres. |
| canal and pit water | one surface per connected body; mouseover shows depth (surface minus floor) and litres |
| pumps (per pulse) | `TankUnitsPerLevel` = 10,000 → 1 kL per notch; `PourLevels` against the dump rate in units |
| hoses | `hoseLitresPerCell` **5 L** (setting; a ~65 mm hose 1.46 m long holds 4.8 L). The old 0.2 units was 40 L a cell. A hose is a container, so it gets a real size. `heldUnits` migrated. |
| tank-to-tank settle, Dump drain | `tankLitresPerCycle` 2,000 L, `dumpLitresPerCycle` 1,000 L (= the old 10 and 5 units) |
| spills / filth | `litresPerFilth` 400 L (= old 2 units) |
| containers, bottles / drink / wash | litres above; drinking and washing consume whole items (no units) |
| converters / stills / works (`CompLiquidConverter`, `LiquidConversion`) | `inputLitresPerDay`, `distillInputLitres`/`distillOutputLitres`, `inputLitres`/`outputLitres`/`productCount`. **Every number is the old value × 200 L**, so rates and ratios are unchanged (a solar still at 6,000 L/day). **OWNER CALL** if machines should get real-world rates too. |
| reaction vat (`RM_LiquidReactionDef`) | `litresA`/`litresB`/`productLitres`/`productCount` (×200 L) |
| liquid bath recipes | `litresPerCraft` 1,000 L (= old 5 units) |
| VE pipe adapters | `litresPerRareTick` 2,000, `resourcePerLitre` 0.005 (1 VE item per 200 L, as before) |
| ruins' starting stock | at least one notch |
| map controls (Source / Sink / Level holder) | count notches (unchanged); inspect adds litres; `RateLabel` says a notch is 1 kL |
| subsurface drill reserve | fill-units of notches (unchanged); report in litres |
| liquid heat, fire burn | notches (burn rate now one rate per square, 0.5 m a day; see `flowworks_unified_depth_2026-10-17.md` §5.6) |
| Dubs Bad Hygiene bridge | terrain tags and drinkable items only, no units (unchanged) |
| ExplosiveGrowth irrigation | no FlowWorks unit use found (`grep` 2026-10-16) |
| other mods | Cauldron gas tap: one banked unit = 200 L into tanks via `RM_Volume.Units`. LuminousPigment GlowTank: one draw = 200 L, read by reflection off `RM_Volume.Units(float)`. WreckedMachines distillation module XML in litres. |
| mod settings text | tank slider says kL; pump text says a notch is 1,000 L (a cubic metre) |

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

- Dug canals and pits read their fill in notches.
- Natural water reads its bed depth (`BedLevelsAt`), scaled by the pond's fill when the pond is limited.
- The setting `mouseoverDepthEnabled` (on) switches it off.

Not yet seen live.
