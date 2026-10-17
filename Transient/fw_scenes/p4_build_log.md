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

## Stages (c)+(d)+(e) — ONE commit (they share RM_MapComponent_Excavation / RM_LiquidStock / RM_LiquidFire; no
## non-interactive way to split hunks in this clone)
### (c) "five" deleted; pond budget slider deleted (+migration); one burn rate; bed settings in metres
- status: DONE
- `sourceBudgetMultiplier` deleted (D4): setting, UI, Scribe, Independent list, site_spec/validation_v2/human_review/
  review_map_coverage tables; `RM_Volume.BodyCapacity` has no multiplier. Migration: `RM_pondBudgetModel` (0 on an old
  save) -> `RM_LiquidStock.MigrateBudgetMultiplier`: a pond formed at x!=1 is re-sized from its floor keeping its fill
  fraction, one log line per pond.
- One burn rate (D3): `burnDaysPerNotch` (default 1 day per 0.5 m) replaces canal+source rates; an old settings file's
  `canalBurnDaysPerLevel` is read once by XML node (the 5-day pond rate is dropped). `TicksPerSourceLevel` deleted.
- Lake floor ceiling (absorbed LAKE_FLOOR_TUNE): `deepBedMaxDepth` slider 2 m .. 125 m (`RM_BedMath.MaxBedCeiling` 250
  notches), shown in metres; default stays 20 notches = 10 m until LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (R11).
- `volumePerTile` pinned to 1 (FluidDef.ConfigErrors refuses anything else).
- Every 5:1 text gone (FlowWorks_Fluids.xml, RM_LiquidStock/StockMath/LiquidBody/FlowKernel/FluidDef/FireMath/LiquidFire,
  settings labels; "buckets hold five bottles, barrels twenty-five" was also wrong: now 15 L / 208 L). Settings text in
  metres (burn, lake floor, slope, sources); Keys ramp/climb strings in metres (the hard-coded "3" now an argument);
  Level Holder inspect in litres; `RM_PumpMath.PourLevels` stale comment fixed.
- Test staging that replaces the slider: `RM_NorthstarProofs.ProofSetBodyFraction("x;z;frac")`; extensions plot D uses
  it (mock-tested; refusal -> UNMEASURED).
- `RM_depthViewModel` marker (spec §9): on an old save every wet dug square is re-pictured once by its metres.
### (d) whole-notch readers re-pointed to decilitres
- status: DONE
- Pump intake: a dug cell with any dL is drawable; takes `min(notch, cell dL)` via `TryTakeDl` (4.5 cm = 900 dL pumped).
  World-to-world outflow still moves whole notches (the outlet pours a notch).
- Burn: `BurnableFluidAt` sees a sheet; canal squares burn `RM_FireMath.DlDue` decilitres per pulse (`BurnOffDl`), a 4.5 cm
  sheet in 22 pulses; detonation consumes the part-notch too; pond squares debit their body at the same rate in dL.
  Exact-level off keeps the old whole-notch path.
- Drowning/toxin: fill = cell dL / notch (fractional), same rate law (P7 owns the relative "over the head" rule).
- Heat: dug cells by dL; natural squares by their REAL water (`NaturalWaterDlAt`: pond surface over the floor), not a flat
  2 (balance note: a 10 m lake square now pushes 10x what it did; strength stays PROVISIONAL).
- Left on whole notches (not in this brief; P5/P7/P14 territory): `RM_ExcavationWalls`, `RM_FlowDoors`, `RM_PitStepCost`
  wet test, `RM_PitScorch`, world-to-world pump outflow, Level Holder pours.
### (e) P8 data side: the readout + the limitless mark
- status: DONE
- `RM_Volume.Readout(hole, ledge, dL)` = "Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)" (floors to 0.5 m, water two
  decimals, litres "#,0"); `LimitlessReadout` = "Open water, never runs dry (about 2 m deep)" (item/spec §4.3 wording;
  the brief's "limitless / never runs dry" paraphrase was not used). `RM_MapComponent_Excavation.DepthReadoutAt(c)`: dug
  square = its dL; limited pond square = `RM_LiquidStock.SquareWaterDl` (one surface from the exact kernel's histogram,
  cached per pulse) over its floor; dried bed = hole, 0 water; limitless (formed body's sticky flag, else river/ocean
  terrain) = the mark, never litres. Ledge = shallowest cardinal hollow between the hole and the ground.
- Mouseover uses it (dry dug squares now show "Water 0.00 m"); bridge-readable `RM_NorthstarProofs.ProofReadout("x,z")`.
- No new art. Texture re-keying of the fill looks (Half still draws chest-deep) is for P9's review.

## Tests (final tree)
- SelfTest 500/500 (`Rewire_fill_look_is_metres_of_water`, `Rewire_five_is_dead_and_nothing_multiplies_a_pond`,
  `Rewire_thin_sheets_are_pumped_burned_drowned_and_warm`, `Readout_two_numbers_and_the_limitless_mark`,
  `Volume_one_ruler_scheme_A`, fire test rewritten to one rate).
- Differential kernel == PulseOracle 3000/3000 in depth, surface, levelset, shipped, pond, exact, exactpond.
- vv_shipped_matrix --skip-ep: SHIPPED kernel_fuzz 0/10000, fills_from_limitless 0/10000, surface_random 0/1000, seq_* 0,
  hose 0/2798, trail 0/1500; control 194/2000 vs 0/2000; VERDICT FAIL only on BENCH's AUTHORED
  `Thirst_slime_last_resort_ruled` (known). OFF_edgeSinksEnabled kernel_fuzz 142/2000 (known harness red).
- FlowWorks python selftests: every red equals the a54be1db6 baseline (extensions thirst toggles, northstar
  RM_ThirstSettings, human_review, hose_port, review_map RM_WaterThin.png coverage); fuel_moat 9/9 after its pattern update.

## NEXT pointers
- `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` — built offline; NEXT: live driver deploys the DLL, loads a pre-rewire save (back up
  Saves first) and reads the three migration log lines (pond budget, depth view, level model) and a mouseover/ProofReadout.
- `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` — data side built; NEXT: P10 walk reads ProofReadout over a dug cell, a filled
  canal, a pond, a dry cell and a sea square (L2), and the owner looks at the wording (V8 veto-able).
