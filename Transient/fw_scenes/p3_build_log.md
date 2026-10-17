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
- status: DONE (on the tree merged with BENCH's thirst commits; DLL rebuilt there by winbuild.py)
- SelfTest 492/492 (12 `Exact_*`). Differential kernel == PulseOracle 3000/3000 in depth, surface, levelset, shipped,
  pond, exact, exactpond. `selftest_level_water.py` 0 failures.
- `vv_shipped_matrix.py --skip-ep`: SHIPPED (levelExactEnabled=1) kernel_fuzz 0/10000, fills_from_limitless 0/10000,
  surface_random 0/1000, seq_* 0, hose 0/2798, trail 0/1500; negative control 194/2000 shipped, 0/2000 authored -> VERDICT
  PASS (run with --skip-suites; the full run's only suite red was AUTHORED `Thirst_slime_last_resort_ruled`, BENCH's).
  Fix: the control now forces only the shipped fields the pre-fix kernel declares (it refused `levelExactEnabled`).
  Pre-existing harness red, not new: OFF_edgeSinksEnabled kernel_fuzz 142/2000 (163-164/2000 in every run since 10-16).
- Made exact-aware: FlowKernelFuzz totals/sink/bounds/snapshot, SurfaceRandomScenesSettleAndConserve (dL step check).

## Stage (d) — northstar level_surface_bar.py per-body surface-gap bridge-readable method
- status: DONE
- `RM_NorthstarProofs.ProofLevelSurface("x,z,w,h"|"-")` via jawa/static_call -> "OK n worst G m;x,z:sq:gap:min:max;...".
- `northstar/level_surface_bar.py` reads and parses it (UNMEASURED on an older DLL, a non-OK answer, or no water); its
  selftest proves the read can go red. Never run live (no bridge, by brief).

## Stage (d) — northstar level_surface_bar.py per-body surface-gap bridge-readable method
- status: pending

## NEXT pointers
- `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` — built offline; NEXT: live driver deploys the committed DLL and runs
  validation.py chain `water_level_surface` on S5/S6 (P10 walk), backing up Saves first (save migration logs per body).
- `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` — whole-notch readers remain; NEXT: re-point pump intake, burn, drowning, heat and
  mouseover to WaterDlAt so a sub-notch sheet can be pumped/burned/read.
