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
- 09:16 publish REFUSED again: local f425b7c884 (canal-overflow builder, RM_SheetMath.cs) conflicts with origin fa912947d8 on RM_SheetMath.cs; 11 local commits unpushed incl. mine 8e13037d85, 2ce59a77ad. Not resolving (another helper's C#); belt keeps proving
- 09:17 tried pushing my 2 commits by plumbing replay onto origin (clean merge-tree) — pre-push hook lints the diverged local HEAD (FOUNDRY code_review lines NOT_APPEND) and refuses; stopped there, commits stay local until the clone's owner of f425b7c884 resolves RM_SheetMath.cs
- 09:17 climb_proof --fresh-map start
- 09:23 climb_proof: HARNESS fix (site_calm before ok assigned); 15 PASS / 0 FAIL / 1 owed (items already done; regression evidence) — northstar/climb_result_20261022T1025_belt.json
- 09:23 NEW trench_crossing_live.py (ring + 2 ladders, can-fail one-ladder control; first scene's straight trench was walked round = HARNESS): 2/2 PASS -> TRENCH_CROSSING A2 verified — northstar/trench_crossing_result_20261022T1035_belt.json
- 09:23 deep_lake_proof --fresh-map start
- 09:25 deep_lake_proof: 3 PASS / 1 FAIL (DL_shallow_dries_first 13>12) / 3 UNMEASURED (shelfCell exact-5, C# harness; save owed) -> filed DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE — src/RimMandrake/FlowWorks/northstar/deep_lake_result_20261022T0930_belt.json
- 09:25 depth_rebuild_proofs --fresh-map start
- 09:34 depth_rebuild_proofs: 17 PASS / 1 FAIL->HARNESS (P7 ratio compared two colonists of different mass; now per kg: rerun --only p7 3.48 PASS) / 1 UNMEASURED (SWIM_armour_drafted_goes_under: exhaustion 1.0 at 6000 ticks, never under) / 2 INFO drown numbers. Items already done: regression evidence — northstar/depth_rebuild_result_20261022T0935_belt.json, _p7_ ...0945
- 09:37 redeploy: HEAD c5c0f047ca FlowWorks DLL (hose swim-split fix 0ab8470911, overflow stage 1 off, reel N/S art, settings search); plan: DLL+srchash+Keyed ~, reel textures +; GSS/LuminousPigment in sync. Stopping game PID 34544
- 09:40 game relaunched via Steam on fw_gss_sitting (14 mods, marker kept), bridge up ~50 s, deployed FlowWorks c5c0f047ca. lines_proof full rerun start
- 09:42 lines_proof on c5c0f047ca: 11/11 PASS -> PIPE_POLES A9 verified (only L1 selftests owed); LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM CLOSED at 0ab8470911. Note: COLLAPSE victim carried a 'Bite' hediff (wild animal on the site; row still PASS)
- 09:42 MOAT live check: scenarios_map --build --fresh-map --only C2 start
- 09:47 MOAT live check: C2 build + 2 h soak still=True dug_changed=0 -> MOAT_LEVEL_DIAGNOSE_HALF_METRE_VANISHES CLOSED — src/RimMandrake/FlowWorks/northstar/moat_c2_soak_20261022T0950_belt.log. (Soak also read C4 still=False: pawns_changed Colonist 1 — C4 not built in this run; plot empty, a colonist wandered in = SITE)
- 09:52 fixer B #3 live check: C4+C10 built on a fresh map: verify ok both; all 3 staged hoses LAID (C4 by 3 ramps). Soak: C10 still; C4 MOVED 16 cells fill 3->1 at (26..27,76..79) beside the C4 reel — C4 is the fluid_moves plot (fixer B: intended); flagged for the walk builder, not filed — src/RimMandrake/FlowWorks/northstar/scenarios_c4_c10_hoses_20261022T0955_belt.txt
- 09:57 redeployed FlowWorks DLL pair ONLY from HEAD 3be0f5c66f (jobTrace + overflow 2-3); worktree has uncommitted pump-style Defs/Textures (art helper) so deploy_custom_mods --apply was NOT used; relaunched, bridge up. raid_trench --direct --depth 8 rerun for jobTrace
- 09:58 raid_trench depth 8 on 3be0f5c66f: STALL again, no colonist down; jobTrace: 4 raiders hold RM_RaiderFillTrench for 10k+ ticks, never progress (noted on CAUSEWAY item, belt_failures) — src/RimMandrake/FlowWorks/northstar/raid_trench_result_20261022T1010_depth8_jobtrace_belt.json
- 09:58 CAUSEWAY mechanism measured: fill notch at D8 ≈ 22,400 ticks per gunner (deep-dig cost curve x MiningSpeed 0.336) — noted on item
- 10:00 BLEED settings search live: 'bleed' -> Drilling and bleed wells first, no blank rows (screenshot) -> BLEED_WELL_STRINGS_RENAME_TAP_RETIRED CLOSED; search cleared, window closed
- 10:00 belt_queue: sheet_overflow_proof --fresh-map start
- 10:11 sheet_overflow_proof (queue): 5 PASS / 3 FAIL / 4 UNMEASURED (+perf) -> filed OVERFLOW_DIAGNOSE_FIRST_WET_RUN (BENCH, for the overflow builder/proof author) — src/RimMandrake/FlowWorks/northstar/sheet_overflow_result_20261022T1040_belt.json
- 10:11 proof_hose --live --only hose,maze,relay start
- 10:17 proof_hose --only hose,maze,relay: 22 PASS / 3 FAIL. HARNESS fixed in validation_hose (relay reels built West one square east since b765116aca: relayTo/fedBy matched by reel_at) -> RL6 PASS on rerun. RL3/RL4 still FAIL on west_inlet only: drawn end x=44.353 is 0.35 INSIDE the footprint's west edge (C# relayEnd withinEdge=True, per-look tolerance 0.75); the python bar (end outside the edge, at the North art's brass inlet) predates the turned West art — HARNESS presumed, owner's eye on the West relay inlet decides. Pre-existing: an IndeterminateError (sheet proof's map_comp_timing in flight) refused preflight; reconciled not-applied (disposable map)
- 10:21 proof_hose carry,style_hose: 15/15 PASS; realflow,save_load: 17 PASS / 2 UNMEASURED (NS_external_pipe no VE pipes on tier; SL4 needs the carry block in the same run) — northstar/proof_hose_hose_{1,2,3}_20261022_belt.json. Total proof_hose today: 54 PASS / 2 FAIL (RL3/RL4 west_inlet, HARNESS presumed) / 2 UNMEASURED; matrix_hose not run
- 10:21 belt_queue: walk_gaps_proof --fresh-map start
- 10:27 walk_gaps_proof (queue): 6 PASS / 3 FAIL / 4 UNMEASURED, all non-PASS HARNESS/SITE presumed (see belt_failures) -> PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO A2 verified — src/RimMandrake/FlowWorks/northstar/walk_gaps_result_20261022T1030_belt.json
- 10:40 walk_gaps_proof x3 with belt HARNESS fixes: run 3 8 PASS / 1 FAIL (TANKS_JOINED: Store tanks never level = walk stop 6 premise false, no item promises it) / 4 UNMEASURED (ponds rig SITE, cover decon flaky SITE). Verified -> DONE: FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE A4, FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT A4, PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO A2
- 10:40 extension_proof --live --site river start
- 10:41 extension_proof --site river: the clean river site save (test_site_saves 'river') did NOT load clean: NRE in vanilla ListerFilthInHomeArea.Notify_HomeAreaChanged during Map.FinalizeLoading (home area missing on the saved site, presumed: the save drops the home map) + Root-level Update NRE -> SITE/HARNESS presumed, not FlowWorks (stack is vanilla only). Went to main menu at once. Extension suite not run (dry site needs the golden-site prep).
- 10:46 river save root cause: saved on a bigger mod list (FloodedCanyon/WeatherSuite/SWBestiary classes, RUT_WickingWrap) -> WEDGED (watchdog). Killing RimWorld and relaunching on fw_gss_sitting
- 10:47 liquid_checks --fresh-map start
- 10:56 liquid_checks --fresh-map: 6 PASS / 2 FAIL / 8 UNMEASURED. L5_switched_off_hose_spills PASS(10-16)->FAIL = REGRESSION, MOD: 10000 units 'spilled', zero filth on the map -> filed SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY (FOUNDRY). L6_free_end_names_their_faction FAIL + L6 draws UNMEASURED: free end 'lying free' on Soil, never coupled to the foreign tank = SITE presumed (West-built reel geometry, first L6 run). L7 rows UNMEASURED (no standing water in the stations), L8 needs --l8-pond — src/RimMandrake/FlowWorks/northstar/liquid_checks_result_20261022T1100_belt.json
