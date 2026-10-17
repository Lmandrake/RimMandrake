# P4 build log — LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD, then P8 data side (FOUNDRY offline builder, 2026-10-17)

Base: origin/main a54be1db6 (P3 exact-level engine 7b2fbe7a0). No bridge, no game.

## Stage (a) — RM_Volume constants (SquareAreaM2, MetresPerNotch, derived litres), glossary; Python reads C#
- status: DONE
- `RM_Volume`: `SquareAreaM2 = 2`, `CentimetresPerNotch = 50`, `LitresPerNotch` = their product (old names
  `LitresPerLevel`/`MetresPerLevel` alias it), glossary (notch / square / yardstick / level / litres); lakebed thresholds
  in metres (`DeepBedMetres 2`, `AbyssBedMetres 4`).
- Python reads C#: `level_water.METRES_PER_NOTCH`/`SQUARE_AREA_M2`, `pond_pump.UNITS_PER_LEVEL`, `liquid_checks.LEVEL`/
  `UNITS_PER_LITRE`, `selftest_conservation_roundtrip` (via `level_water._volume_const`, which resolves products).
- Tests: SelfTest 496/496 (+`Volume_one_ruler_scheme_A`); level_water, pond_pump, liquid_checks, conservation 13/13 PASS.

## Stage (b) — FillTier by metres of water; labels in metres; LiquidLooks tier map
- status: DONE
- `RM_ExcavationDepth.FillTier(long dL)` = `RM_LevelSolve.LookBand` (by metres of water; the hole is not an input); the
  fraction thresholds and `FluidDef.FillTerrainFor(tier, depth)` deleted; `LabelOf` in metres ("1.5 m", "pit 2 m").
- `ApplyFillTerrain`: ONE rule for every dug square, canal or pit, exact or not.
- **Part-filled pit rule** (feasibility §T1 row `FluidDef.cs:145`: "fill look per the ruled water bands, by water depth,
  not hole depth"): a pit shows its water's look (4 cm = the very-shallow hook); its route cost stays a pit's by a new
  prefix `RM_Patch_WetPitPlanningCost` (a wet pit cell costs at least `RM_Channel_Superdeep`'s 300, after the cover's
  prefix). Capture/hold/climb read the grid (ruling 26), unchanged.
- Labels (defNames unchanged): fills "knee-deep <liq> (under 0.75 m)" / "shallow (about 1 m)" / "chest-deep (about
  1.5 m)" / "deep (2 m or more)" (52 terrains); dug "canal (0.5 m)" / "canal (1 m)" / "canal (1.5 m)" / "pit (2 m or more)".
  Textures NOT re-pointed (Half still draws the chest-deep ramp): re-keying textures is a look change for P9's review.
- `RM_LiquidLooks.FluidMembers` surface tiers follow metres: 0.5/1 m shallow, 1.5 m chest, 2 m+ deep (+ very-shallow hook).
- Mirrors: `review_map.fill_tier`, `validation_v2._fill_tier`/`fill_cost_findings` (bands 2..4), look_canal station text.
- Tests: SelfTest 497/497 (+`Rewire_fill_look_is_metres_of_water`); looks_round PASS; northstar selftest only the
  pre-existing BENCH `RM_ThirstSettings` red. Baseline (a54be1db6, scratch clone) already red, unchanged by this stage:
  selftest_extensions (thirst toggles), selftest_human_review, selftest_hose_port, selftest_review_map (RM_WaterThin.png
  coverage).

## Stage (c) — "five" deleted; sourceBudgetMultiplier deleted (+migration); one burn rate; bed settings in metres (cap to 125 m)
- status: pending

## Stage (d) — whole-notch readers re-pointed to dL (pump intake, burn, drowning, heat, mouseover)
- status: pending

## Stage (e) — P8 data side: readout string + limitless mark
- status: pending

## Tests
- pending

## NEXT pointers
- pending
