# FlowWorks C — unbuilt rows build pass (2026-10-05)

## Rows

## Log
- [start] 10 UNBUILT rows = v2 register (northstar/validation_v2.py UNBUILT dict). Source census:
  - fill_fluid_distinct: LIQUID_BODY_FLUID_IDENTITY_1 — fluidGrid+no-mix BUILT; predicate stale (activeFluid kept as fallback)
  - pawn_height_ladder_legible / pawn_lowers / pawn_rises / pit_trapped_reads_as_trapped / slime_occupant_below_surface: PIT_DEPTH_DRAW_OFFSET_1 — RM_PitDepthDraw.cs BUILT; predicate regex stale
  - ladder_state_legible: LADDER_PRISON_DOOR_1 (closed cf789dc80) — RM_CompLadder.raised BUILT; predicate stale (thingClass)
  - pit_covered_invisible / seam: PIT_COVER_FALL_REWIRE_1 (closed 9d6cefabd) — check cover
  - tar_fill_front_lags_water: FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity — GENUINELY UNBUILT (pulse engine uses global FlowPerPulse)
- [C#] viscosity built: RM_StockMath.ViscosityStride/FluidMovesThisPulse + PickDonor gate + scribed pulseCount + setting viscosityEnabled; RM_PromotionProofs.cs (ProofPawnSink/ProofLadder/ProofCover/ProofFluidRow); winbuild OK; C# selftest 79/79
- [py] v2: UNBUILT emptied -> PROMOTED table (O3 guards rows exist); X scenes; phase_X rows X1-X9+X7n; P4b ladder raise/lower; oracle fluid+no-mix+viscosity; site_spec viscosityEnabled. next: mock
- [py] mock GREEN 74 rows; offline O1-O10/O-NEG/O-LIVE-NEG PASS (32 faults); validation.py +viscosityEnabled toggle (tar_front component); northstar selftest 36 toggles PASS. running run_selftests
- [done] PUBLISHED 5d5e6cc12 (code) + ledger notes; run_selftests 182/182; C# 79/79. Rows still owed: a LIVE v2 run (bridge) - all 10 promoted rows are mock/offline-proven only
