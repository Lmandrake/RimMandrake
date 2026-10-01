# FOUNDRY live-session defect fixes, 2026-10-01 (progress)

| item | state | note |
|---|---|---|
| STILLSAND_LOAD_DEF_ERRORS_1 | closed 937aba350 | TreeCategory Full, Trainability Intermediate, StartingHediff severity, FrontLegs split L/R (Cauldron, TheForge), meat->Megaspider, Contagion Graphic_Random->Single |
| OORRIK_PAWNGEN_NRE_1 | closed c86ba25f6 | body "Rat" does not exist -> QuadrupedAnimalWithPaws |
| SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1 | closed 2d1886be8 | filth placementMask Unnatural; corpse kept, letter reworded |
| SOORRAK_FLIGHT_JOBSTART_NRE_1 | closed 99163e0e7 | prefix guard for pooled job (def null) |
| RIMPLACE_GENSTEP_NRE_1 | closed bb2631aaa | def null as selector option; plan path fallback |
| selftests | 78/81 | known fails only: selftest_sound_paths.py, walklint (Pyrelands BAD_PACKAGEID) |

Live proof: STILLSAND_FIXES_LIVE_PROOF_1.
