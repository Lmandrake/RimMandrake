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

## Results (rows PASS/FAIL/UNMEASURED, final run of each, MEASURED from the result JSONs)
- lines_proof 11/0/0 (c5c0f047ca) · drawbridge_proof 12/0/0 · suspension_bridge_proof 26/0/8 (+ waters lake/sea PASS on painted water)
- trench_cover_proof 6/0/4 owed · trench_blast_live 1/0/0 · trench_cast_live 2/0/0 · raid_trench_proof depth 4: breach PASS; depth 8: causeway FAIL (MOD); --jump-packs PASS
- raid_ladder_live 4/0/0 · raid_siege_live 2/0/0 · trench_crossing_live 2/0/0 · climb_proof 15/0/1 owed · depth_rebuild_proofs 17/0/1 (+p7 PASS)
- deep_lake_proof (ee9fa61fbc) 5/2/1 (refill hash regression) · validation_v2 61/0/1 · proof_hose blocks 54/2/2 (RL3/RL4 west-inlet bar) · liquid_checks 6/2/8 (L5 spill regression)
- pond_pump 2/0/1 · thirst T4,T5 2/0 · sprinkler T22 1/0 · walk_gaps_proof 8/1/4 · sheet_overflow_proof 5/3/4 · pit_rescue_live 1/1(+assist)/0+1 · suspension_settings_live 1/1/0
- scenarios: C2 moat 2 h soak still; C4/C10 hoses laid; bleed settings search PASS

## Items verified / closed / filed
- CLOSED/done: SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN, LADDER_HOSE_DIAGNOSE_RETRACTS_ON_A_WHIM, MOAT_LEVEL_DIAGNOSE_HALF_METRE_VANISHES, BLEED_WELL_STRINGS_RENAME_TAP_RETIRED, PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO, FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE, FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT, SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING, TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT
- verified (criteria): PIPE_POLES A7 A8 A9 A10 · DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS L2 run · SUSPENSION_BRIDGE_BUILD_POSTS A1-A6 · GRATE A1-A3 · UNDERPASS A1-A6 · JETTY A1-A2 · ART_RESKIN A3 · WATERS A2 A4 · RAIDERS_TRENCH A2 A4 A5 A6 A7 · TRENCH_CROSSING A2 · LIQUID_LEDGER A5
- FILED: CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (mechanism: fill notch ~22k ticks), DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE (fixed by fixer E; refill hash now FAILs), OVERFLOW_DIAGNOSE_FIRST_WET_RUN, SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY (regression), SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING
- DROPPED (my wrong filing): RESCUE_LADDER_DIAGNOSE_FRAME_NOBODY_FINISHES — the rescuers had Construction priority 0 (SITE)


## NEXT
- Deployed FlowWorks DLL = HEAD ee9fa61fbc (deploy_custom_mods FlowWorks --apply, worktree FlowWorks was clean). Tier fw_gss_sitting 14 mods, marker deployed/config/ModsConfig.swap-active.json kept. companion_profile test until 2026-10-23T07:00Z.
- Waiting on fixers for re-prove: CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP (raid_trench_proof --direct --depth 8), SPILL_DIAGNOSE_TEN_THOUSAND_GONE_DRY (liquid_checks --only L5), DRAWDOWN refill hash (deep_lake_proof --fresh-map), OVERFLOW_DIAGNOSE_FIRST_WET_RUN (sheet_overflow_proof --fresh-map), SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING (suspension_settings_live.py).
- On any new FlowWorks DLL commit: plan deploy, game down, --apply only when `git status src/RimMandrake/FlowWorks` (non-py) is clean, else copy the committed DLL pair only (git show HEAD:...), relaunch via Steam, rerun lines_proof + the item's proof.
- Owed, unscripted or blocked: SUSPENSION_WATERS A1 (no river tile with a fast lane), A3 flood (decks never awash), GRATE A4 slime, PIT_TEMPERATURE A2-A4, HOSE matrix width bar (re-baseline after his girth pick), walk_gaps PONDS rig (proof author), extension_proof (preflight refuses on this tier/autosave).
- End of day: reload RM_fw_walkthrough_20261022 (load-checked clean at ~12:26), `bridge take --force --for "holding for the owner's walkthrough"`.
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
- 10:56 pond_pump --fresh-map start
- 11:08 pond_pump: HARNESS fixes (no site_calm after fresh map -> Hive stopped arm; unfed colonists Starving in the multi-day refill wait -> feed per chunk); run 4: 2 PASS / 1 UNMEASURED (draw receded no cell) — northstar/pond_pump_result_20261022T1115_belt.json
- 11:09 thirst_live T4,T5 PASS (salt 0.695x) + sprinkler_live T22 PASS -> SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING A1/A2 verified (L3)
- 11:10 publish blocked: another helper's dirty OWNER.jsonl vs origin (reset --keep refused); my e7c05788f9 local, retry later. river_site.py for SUSPENSION_WATERS rows start
- 11:12 river_site.py: 13 river tiles tried, all rejected 'no current with a fast lane' (fast=0) -> no river map; WAT_river/lake/sea rows stay UNMEASURED (SITE)
- 11:12 validation_v2 --live --fresh-map start
- 11:15 redeployed FlowWorks from HEAD ee9fa61fbc (DRAWDOWN fix + shelfCell, pump looks committed, pipe atlases) via deploy_custom_mods --apply (worktree FlowWorks clean); relaunched
- 11:20 validation_v2 --live --fresh-map on ee9fa61fbc: 61 PASS / 1 UNMEASURED (S6_digToDepth_gate: probe cells fogged, SITE), 323 s — northstar/validation_v2_result_20261022T1145_belt.json. deep_lake rerun for DRAWDOWN fix
- 11:24 deep_lake on ee9fa61fbc (HARNESS: wetnessCutoffEnabled off for the run): run3 4P/2F (hollow: abyss 0 on a flat map = SITE; refill hash FAIL), run4 5P/2F (refill hash FAIL again, walks_out FAIL) -> noted on DRAWDOWN item as a probable regression of the refill
- 11:25 NEW trench_blast_live.py: 6/6 trials trench 20.0 = open 20.0 -> TRENCH_COVER A4 verified (only A3 raid-in-canal owed) — src/RimMandrake/FlowWorks/northstar/trench_blast_result_20261022T1135_belt.json
- 11:30 NEW trench_cast_live.py: run1 PASS/PASS (sheer canal too far: closest 6, moved beside), run2 SITE (rerun re-deepened: ProofResetRect added), run3 PASS/PASS (casts from 1 m canal; sheer canal closest 1, never entered) -> TRENCH_COVER A3 verified — src/RimMandrake/FlowWorks/northstar/trench_cast_result_20261022T1150_belt.json
- 11:32 NEW raid_ladder_live.py: run1 3/4 (HARNESS: read 'held' = any sheer pit; the faction-aware field is 'trapped'), run2 4/4 PASS -> RAIDERS_TRENCH A6, A7 verified (A3 fill = CAUSEWAY item, A4 jump-pack, A5 siege still owed) — src/RimMandrake/FlowWorks/northstar/raid_ladder_result_20261022T1200_belt.json
- 11:36 NEW raid_siege_live.py: run1 FAIL = HARNESS (a raider took RM_RaiderSetLadder in the instant it joined the assault lord, before the switch to LordJob_Siege, and kept it: trench rules now off across the swap); run2 2/2 PASS (sieges build, no trench jobs) -> RAIDERS_TRENCH A5 verified. LEAD (minor, not filed): a trench job is not re-checked when its pawn's lord stops being eligible — src/RimMandrake/FlowWorks/northstar/raid_siege_result_20261022T1210_belt.json
- 11:41 raid_trench_proof --jump-packs (new flag: wear Apparel_PackJump; colonists boxed so they are not shot down first): jump1 SITE (equip!=wear, colonists downed), jump2 PASS but MASKSWAP/LADDER mis-scored (HARNESS: jump crossing is legal), jump3: RAID_JUMP_LANDS_UNHURT PASS -> RAIDERS_TRENCH A4 verified (only A3 fill = CAUSEWAY item remains) — src/RimMandrake/FlowWorks/northstar/raid_trench_result_20261022T1225_jump_belt.json
- 11:47 liquid_checks evidence -> LIQUID_LEDGER A5 verified (ship tank fill/empty). Suspension WATERS on painted water (current map): --lake (18-wide WaterDeep, tower) PASS -> A2 verified; --sea first on a 6x5 patch PASSed with decked=0 (path went AROUND: HARNESS, row now requires decked>0), then a map-long 6-wide WaterOceanDeep strip: decked=6 PASS -> A4 verified. River row needs a real current (no tile qualified); flood row SITE (flood water goes into the dug trench, decks never awash)
- 11:50 NEW suspension_settings_live.py: SB_settings_off_never_breaks PASS (Over 645/600 kg, 120 ticks, 6 decks stand); SB_settings_off_no_button FAIL x2 (11 designators still visible=True per list_architect_designators with the setting False) -> filed SUSPENSION_BUTTONS_DIAGNOSE_STILL_SHOWING (MOD vs instrument undecided). A7 not verified (half) — src/RimMandrake/FlowWorks/northstar/suspension_settings_result_20261022T1300_belt.json
- 12:01 NEW pit_rescue_live.py (PIT_ACCESS A4) x4: ladder QUEUED at 250 ticks (PASS), frame wood delivered but never finished unassisted (FAIL x3 -> filed RESCUE_LADDER_DIAGNOSE_FRAME_NOBODY_FINISHES, FOUNDRY); with an ordered FinishFrame (assist) the ladder stands and the downed colonist is carried out (+1500); control on open ground rescued at +1250 — src/RimMandrake/FlowWorks/northstar/pit_rescue_result_20261022T1330_belt.json
- 12:03 proof_hose --only matrix_hose: 9/9 MX rows FAIL on width only (Flat 0.18 vs spec 0.375-0.385, Plump 0.23 vs 0.46-0.47; width_over_wire 2.88/3.68 vs >=4): GSS northstar_matrix/design_spec.py:337 predates f256450686 (hose 0.18/0.23, HOSE_GIRTH_TUNE_MUCH_THINNER). HARNESS (stale bar); NOT re-baselined because the girth is the owner's call at tonight's walk — re-baseline to whatever he picks. Every other matrix field passes — src/RimMandrake/FlowWorks/northstar/proof_hose_matrix_20261022T1205_belt.json
- 12:04 loading golden site NS_FlowWorks_TrialSite_v1 (2026-10-05 save) for preflight + extension dry
- 12:05 golden site NS_FlowWorks_TrialSite_v1 loaded clean (0 class/ref errors); preflight live: 11 PASS / 6 FAIL — tier is fw_gss_sitting not flowworks (P-L1/P-E6, expected), VEF new-faction dialog open (closed), autosave 0.25 d (owner's global pref: NOT changed), screen size; LEAD P-S2: the 10-05 save's ponds read capacity=stock 0.4x the manifest (D 50 vs 125, K 8 vs 20, S 32 vs 80) — a units change or an upgrade loss, unproven; extension_proof dry not run (preflight refuses) — northstar/preflight_golden_20261022T1210_belt.log
- 12:16 CORRECTION: pit_rescue 'frame never finished' was SITE — bridge-spawned colonists had work priority 0 (Mining/Construction); with priorities set: pit_rescue_live 3/3 PASS unassisted -> PIT_ACCESS A4 verified; item RESCUE_LADDER_DIAGNOSE_FRAME_NOBODY_FINISHES DROPPED. NEW quarry_find_live.py (same priority fix) PASS -> FLOWWORKS_QUARRY A5 verified
- 12:17 reach_map_proof --fresh-map (WALL_REACH_TUNE A2 REACH_THROTTLE_HOLDS) start
- 12:22 reach_map_proof --fresh-map 6 PASS / 1 owed (REACH_THROTTLE_HOLDS PASS) + residual soak 10,000 ticks: steady WALLREACH ~98/1000 ticks (bar 100; was 890-1010), residual 0 -> WALL_REACH_TUNE_REBUILDS_TENFOLD A2+A3 verified — src/RimMandrake/FlowWorks/northstar/reach_map_proof_result_20261022T1220_belt.json, src/RimMandrake/FlowWorks/northstar/reach_residual_soak_20261022T1225_belt.json
- 12:24 NEW station_reach_live.py: 2/2 PASS -> STATION_REACH_CENTRE_RETHINK_FOOTPRINT A2 verified. LEAD (unproven): channel held 6 notches (2 x 3 squares = 60000 units?) and the tank gained 55000 — 5000 unaccounted (station buffer, soak, or a loss) — src/RimMandrake/FlowWorks/northstar/station_reach_result_20261022T1235_belt.json
- 12:25 NEW jetty_drop_live.py: run1 HARNESS (select_pawn wants 'Thing_<id>'), run2 PASS (gizmos Undraft/Melee/'Jump into pit'; accepted; landed 91,218 on the pit floor, descent fall=9.7) -> SUSPENSION_JETTY A3 verified -> item done — src/RimMandrake/FlowWorks/northstar/jetty_drop_result_20261022T1245_belt.json
- 12:26 owner's RM_fw_walkthrough_20261022 load-checked on deployed ee9fa61fbc: loaded, 25 new log lines, 0 exceptions/errors (not ticked, not saved)
- 12:27 NEW underpass_raid_live.py: PASS (raiders on the floor under the deck at t+180, past it at t+660) -> SUSPENSION_UNDERPASS A7 verified — src/RimMandrake/FlowWorks/northstar/underpass_raid_result_20261022T1250_belt.json
- 12:29 raid_trench_proof --preladder (new flag): RAID_PRELADDERED_CROSSES PASS (island at t+1500 over the two pre-set ladders, no extra ladder) -> TRENCH_CROSSING A3 verified PARTIAL (its second clause is truncated in the ledger) — src/RimMandrake/FlowWorks/northstar/raid_trench_result_20261022T1300_preladder_belt.json
- 12:36 validation_v2 HARNESS fix (S6 probe cells unfogged first) -> --live --fresh-map 62/62 PASS on ee9fa61fbc — northstar/validation_v2_result_20261022T1305_belt.json
- 12:36 thirst_live full (in 3 groups) start on a fresh map
- 12:52 thirst_live full in 3 groups on ee9fa61fbc: 20 PASS / 0 FAIL / 4 UNMEASURED (T1 needs 3 mod lists, T18 needs Dubs, T14 no native animal spawned on this map); T29 wrote no row (the run ended after T26: a downed colonist + a Fingerspike arrival stopped the governor in group C); T6 (60k ticks) and T15R not run — northstar/thirst_live_result_20261022T1320_{A,B,C}_belt.json
- 12:58 sprinkler_live (HARNESS fix: site_calm on a fresh map; Hive stopped arm): 8/8 rows PASS until a ToxicBuildup hurt stopped the governor after acid_hurts_fuel_puddles (SITE presumed: polluted map / acid spray near a colonist; untraced); remaining rows not run — src/RimMandrake/FlowWorks/northstar/sprinkler_live_result_20261022T1335_belt.json
- 13:00 SPILL correction: liquid_checks counted only RM_Filth_LiquidSpill; fresh water spills as RM_Filth_WaterSpill since cad23ba0e1 (HARNESS, fixed). L5 rerun: +2 thickness for 10000 units vs 3 expected, rect already at 5 from the setup's own 20250 units -> item narrowed (note), not closed — src/RimMandrake/FlowWorks/northstar/liquid_checks_L5_result_20261022T1345_belt.json
