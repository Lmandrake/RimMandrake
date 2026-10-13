# POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK

Spec: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` §8, §8.5, §9.6. Owner 2026-10-12: *"1 tank
square, 1 deep water square/pond, 1 deep canal square should all be the same volume."*

## built (BENCH night helper, 2026-10-13, offline)

- `Source/RM_Volume.cs` (Verse-free, in SelfTest): `LevelsPerSquare 4`, `UnitsPerLevel 5`, `UnitsPerSquare 20`,
  `ShallowBedLevels 2`, `BedLevels(impassable, pathCost)` (deep = Impassable or pathCost >= 40: WaterDeep, OceanDeep,
  MovingChestDeep; shallow/marsh = 2), `BodyCapacity`, `TankCapacity(area, tall, mult)`, `MigratedStock`, `Overfull`.
  `RM_PumpMath.TankUnitsPerLevel` is now an alias of `RM_Volume.UnitsPerLevel`.
- Pond capacity = Σ bed levels of the footprint × volumePerTile × budget (`RM_LiquidStock.CapacityOf`, via
  `RM_MapComponent_Excavation.BedLevelsAt`, which reads the live water or the recorded water terrain).
  `FluidDef.canalCellsPerSourceCell` deleted from C# and from every FluidDef XML (13 rows) in the same change.
- Tank capacity = footprint (def size) × 20 × (2 if `RM_LiquidTankExtension.tall`) × tank slider.
  `RM_LiquidTank` 2×2 = 80 (was 300); `RM_UniversalCargoTank` 2×2 **tall** = 160 (was 600) — design §8.2 allowed
  80 or 160; tall chosen so the cargo tank stays the bigger one.
- Save migration (§8.3): `RM_volumeModel` scribed (absent = 1); FinalizeInit rescales every limited body once,
  keeping its fill fraction, one log line per body; limitless untouched. Tanks keep every stored unit; an overfull
  tank refuses input, drains normally, and its inspect line says "overfull (old save)".
- Settings text: pond-budget and tank-capacity labels state the per-square numbers and that a multiplier ≠ 1 breaks
  one square = one square.

## not built here (owed)

- **Tank footprint family + tall twins** (1×1, 1×2, 3×3 and tall versions, §8.5): the capacity machinery takes any
  footprint and the `tall` flag, but the new ThingDefs need art through the art ledger (tall tanks are new art; a
  1×2 cannot honestly reuse the square 2×2 texture) and costs. Not added: cosmetic/art work needs the owner.
- Recession still compares the MEAN per-cell volume; the drawdown that empties the shallow rim first is
  `POND_ELEVATION_BUILD_LAKES_RUN_DEEP` (§9.3).
- Code review: RM_Volume.cs, VolumeChecks.cs, RM_LiquidStock.cs, Building_LiquidTank.cs,
  RM_MapComponent_Excavation.cs are DIRTY (not self-marked).

## criteria
- O1 L0: C# selftest `Volume_one_square_is_one_square`, `Volume_bed_depth_follows_the_water`, `Volume_migration_keeps_the_fill_fraction_and_every_tank_unit`, `Volume_production_wiring` pass (selftest_flowworks_stock.py 288/288)
- O2 L0: conservation model trips 7 (25 deep pond squares fill a 25-square D4 pit exactly), 11 (square = square, every footprint, tall = twice), 12 (mixed pond holds 60 and refills LIFO), 13 (migration) pass (13/13)
- O3 L0: no FluidDef or tank XML sets a deleted field; FlowWorks builds with 0 warnings
- A1 L1: the mod loads with no config error from FluidDef or RM_LiquidTankExtension
- A2 L2: short live check: a fresh 2x2 liquid tank reads 80 units capacity, the cargo tank 160; a freshly classified deep pond of N cells reports capacity 4N (shallow 2N) via jawa/flowworks_body_report
- A3 L2: an old save loads, logs "volume model 1 -> 2", each limited pond keeps its fill fraction, and an overfull tank shows "overfull (old save)"
