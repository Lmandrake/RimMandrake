# P3 build log — WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES (FOUNDRY offline builder, 2026-10-17)

## Stage (a) — Python oracle/reference: level water model + property tests + S1-S6 redrawn
- status: DONE (this commit)
- `src/RimMandrake/FlowWorks/northstar/level_water.py`: the reference. dL truth (U = RM_Volume.UnitsPerLevel, read from C#),
  per-square W, pond `dl` over its floor histogram, fill-and-spill band solve with pond nodes, mouth pace by lambda
  interpolation + canal re-solve, dead band 1 dL/node, sink-hop remainder order, per-body surface-gap diagnostic.
- `validation_v2.PulseOracle(level_exact=True)` delegates its pulse to it (F = W // U kept for old readers).
- `northstar/selftest_level_water.py`: 47 checks, 0 failures. S5.A all ten canal squares 0.237 m, pond surface -0.263 m;
  S5.B all ten at 4.5 cm; S5.E 0.111 m sheet; S5.F 1 m + 1 m; S6 pond 1.444 m x9; S1/S2/S4 timings; split/merge at a sill;
  fuzz 1000 scenes: conservation to the dL every pulse, bounds, gap < 1 mm in all 952 that came to rest.
- Pre-existing, not mine: validation_v2 O-LIVE-NEG red on `lastResortDrinking missing from the table` (thirst setting
  committed by another seat 037fbdf94 minutes before this run).

## Stage (b) — C# kernel (RM_FlowKernel.cs, RM_PondDepthMath.cs, save/load, whole-notch migration)
- status: DONE (source commit; DLL rebuilt on the merged tree in the next commit)
- `Source/RM_LevelSolve.cs` (new, Verse-free): band fill-and-spill solve with pond nodes, pond exact surface, LookBand by
  true metres, RM_SurfaceGap diagnostic. `RM_FlowKernel`: `levelExactEnabled`, `part` grid (W = fill*U + part),
  `RM_ILevelWorld`, `ResolveExact` (port of level_water._exact_component/_domain/_solve_domain).
- Adapter: scribed part grid (`RM_excavationPartGrid`), `RM_levelModel` migration logging canal + per-pond litres
  before/after; pond `stockDl` (long) truth with `stock` as float view (old saves: round(stock*U), no loss); every
  whole-level writer checks room in dL (pump pour, rain, displacement, driver fill); fill look by true metres (pits keep
  their superdeep terrain: passability); StagePond lays the exact surface; head rule stands down when exact is on.
- Setting `levelExactEnabled` (default ON), UI checkbox, settings tables (+1 toggle: 149).
- Hook for the under-25 cm art: `FluidDef.fillTerrainVeryShallow` (null -> 0.5 m look). Readout API for P8:
  `WaterDlAt`, `WaterMetresAt`, `WaterSurfaceMetresAt`, `SurfaceGaps`.
- Tests: SelfTest 490/490 (12 new `Exact_*`); differential kernel==oracle 3000/3000 in all 7 modes (incl. exact,
  exactpond); mutation probe (remainder laid unevenly) turns 6 Exact_* red.
- Known limits (left for P4/P7/P8): whole-level readers (pump intake, fire burn, drowning, mouseover) still read whole
  notches, so a 4.5 cm sheet cannot be pumped or burned; levelUnit != 1 converts with rounding.

## Stage (c) — selftests + vv_shipped_matrix.py at SHIPPED settings + oracle-vs-kernel differential
- status: pending

## Stage (d) — northstar level_surface_bar.py per-body surface-gap bridge-readable method
- status: pending

## NEXT pointers
