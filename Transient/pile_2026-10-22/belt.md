# BENCH prove-fix belt — 2026-10-22

Started 08:48 PDT. Tier fw_gss_sitting, DLL 41fb948b5e. Owner save RM_fw_walkthrough_20261022 untouched.

## Proof → item map
| proof | rows → items (criteria) |
|---|---|
| lines_proof | PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE A4-A10 (A4-A6 verified 10-21); POWER_CORD_* (done); PITCOVER_FIX / PITFALL_FIX (done) |
| drawbridge_proof | DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS rows (RAISE_PATH..RAID_UP, SAVE_MIDRAISE) |
| suspension_bridge_proof | SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS A1-A7, SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN A1-A2, _GRATE_, _UNDERPASS_, _WATERS_, _JETTY_, _ART_RESKIN_ |
| trench_cover_proof | TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT A2-A4; PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH |
| raid_trench_proof | RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP A2-A7; TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP A3; PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH |
| climb_proof | PIT_CLIFF_MASK / PIT_RAMP / PIT_POCKET_GRID rows; TRENCH_CROSSING_FIX A2 (colonist down-across-up) |
| deep_lake_proof | LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (A2 is owner look) |
| depth_rebuild_proofs | FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG, DEEP_WATER_BUILD_SWIM_OR_SINK, PIT_DEPTH_WIDEN_*, RIVER_SWEEP_FIX_* |
| reach_map_proof | REACH_* (done AM) |
| extension_proof | FLOWWORKS_CHECKOUT_SCOPE_1 A2, TESTENV_FLOODS_HARDEN_* A1 |
| proof_hose | PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND A2 (with suspension) |
| level_water | WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES |
| (no script) | FLOWWORKS_RAIL_LADDER_* A4, FLOWWORKS_PIT_TRAVEL_* A4 (no flight), FLOWWORKS_PUMP_PORTS_* A4, PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO A2 — ad-hoc live checks if time |

## Harness fixes
- HARNESS validation_core._prepare_site: plants swept again AFTER reveal (WildPlantSpawner re-seeded one Plant_Grass in the 21x95 lines site during the ~60 reveal ticks). Result: lines_proof 10/11 PASS.
- HARNESS drawbridge_proof._raid_variant: pawns standing in the origin plot vanish BEFORE its buildings are destroyed (destroying a winch crashes a still-raised leaf onto riders = the PM 'Cut/Head' presumed).

## Run log
- 08:48 belt started
- 09:05 lines_proof --fresh-map: 10 PASS / 1 FAIL (LADDER_HOSE_DRAINS_RAISED_STAYS, MOD, same as LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM) — src/RimMandrake/FlowWorks/northstar/lines_result_20261022T0905_belt.json

## Results (rows PASS/FAIL/UNMEASURED)
(pending)

## Items verified / closed / filed
(pending)

## NEXT
(pending)
- 08:49 lines_proof --fresh-map start (validation_core post-reveal plant sweep)
- 08:53 drawbridge_proof --fresh-map start
