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
- 08:58 drawbridge_proof --fresh-map: 12/12 PASS (Fingerspike arrival recovered as SITE) — northstar/drawbridge_result_20261022T0915_belt.json; verified DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS L2 pass (no criteria registered on the item, run recorded only)
- 08:58 commit 8e13037d85 local; ./publish REFUSED: origin fa912947d8 touches RM_SheetMath.cs which another helper has uncommitted in this clone — retry later, not resolving
- 08:58 suspension_bridge_proof --fresh-map start
- 09:04 suspension_bridge_proof --fresh-map: 26 PASS / 0 FAIL / 8 UNMEASURED (5 owed-unscripted, 3 water rows need --river/--lake/--sea, WAT_flood SITE: decks never awash) — northstar/suspension_result_20261022T0925_belt.json. Verified: SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN A1 A2 -> CLOSED; POSTS A1-A6; GRATE A1-A3; UNDERPASS A1-A6; JETTY A1-A2; ART_RESKIN A3
- 09:04 trench_cover_proof --fresh-map start
- 09:04 trench_cover_proof: 6 PASS / 0 FAIL / 4 UNMEASURED owed — northstar/trench_cover_result_20261022T0935_belt.json; TRENCH_COVER A2 verified
- 09:04 raid_trench_proof --fresh-map start
- 09:07 raid_trench_proof (storyteller raid): RAID_island_sealed PASS; outcome MILL_FAR — SITE: LordJob_StageThenAttack staged 62+ out for 15000 ticks, and 2 Entities FleshbeastAssault lords (7 pawns) on the map despite site_calm; MASKSWAP UNMEASURED. Rerun --direct
- 09:11 raid_trench_proof --direct x3: HARNESS fixes (MASKSWAP bar predates RAIDERS_TRENCH ruling -> crossing over raider ladders is UNMEASURED; new row RAID_LADDER_BREACH; bar = ladders on both walls + used). raid_4: RAID_LADDER_BREACH PASS -> RAIDERS_TRENCH A2 verified (northstar/raid_trench_result_20261022T1000_belt.json)
- 09:11 raid_trench_proof --direct --depth 8 (A3 fill causeway) start
- 09:15 raid_trench_proof --direct --depth 8: RAID_FILL_CAUSEWAY FAIL (MOD presumed) -> filed CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (FOUNDRY); MASKSWAP PASS (no crossing). Confound probe: free colonist + 600 ticks, still Wait. Evidence northstar/raid_trench_result_20261022T1015_depth8_belt.json + _probe_ txt
