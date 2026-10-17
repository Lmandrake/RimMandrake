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
- status: pending

## Stage (c) — selftests + vv_shipped_matrix.py at SHIPPED settings + oracle-vs-kernel differential
- status: pending

## Stage (d) — northstar level_surface_bar.py per-body surface-gap bridge-readable method
- status: pending

## NEXT pointers
