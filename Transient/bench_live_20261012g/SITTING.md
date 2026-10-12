# BENCH live sitting 2026-10-12g (pass 6, ratchet pilot EXIT RUN, owner at work)

Pass HEAD **7589d73ef6** (`claude_sha.txt`; includes ash build 3cf1662bbb). `git archive` of ALL of src/ at `D:\Luke\dev\_rmscratch\bench_live_20261012g`.
Tier: 23 mods (ratchet_pilot + mandrake.rm.patches), Steam launch. Owner list restored, md5 ee01dae9e30d121c78d88e474dacd8e8. Game down, bridge released.
Deploy: FlowWorks (RM_ColoredWater.xml) and biomes compose (11 files incl. FireEcologyHook.dll) applied.
Harness faults found and fixed this sitting (no code changed): the JawaBench TEST profile had expired 18:00Z (renewed to 2026-10-13T06:00Z, same keys);
a stale `Biomes/Pyrelands/Defs/TerrainDefs/AshLadder.xml` stayed in the GAME copy after the build deleted it (deploy never prunes) and logged
"XML error: Could not register node RM_FE_AshBase"; removed by hand at 14:00 and the game relaunched. Pyrelands main run 1 = before, run 2 = after.

## Tally at pass HEAD
| suite | result | class of non-PASS |
|---|---|---|
| Ideo worldgen NRE | **0 IdeoFoundation_Deity hits** over 5 quicktest worldgens + 3 Pyrelands site builds (Player.log) | |
| 1 GSS proof_all | **106/106 PASS**, 452 s (proof_all_20261012T122101.json). Run 1: 105 PASS + Z_log_budget UNMEASURED (expired test profile, HARNESS, fixed); a 2nd run was refused by offline gate matrix_selftest C2 until the first run's shots dir was deleted (HARNESS, filed) | |
| 2 FlowWorks validation_v2 | **61/61 PASS**, 14105 ticks, 295 s (v2_20261012g.json) | |
| 2 river extension | **17 PASS / 3 UNMEASURED / 0 FAIL** (ext_river.json) | returns_home, panning_draws_stock, flood_refill: SITE presumed (SWEPT pending=0; pan=nothing), same three as passes 4-5, untraced; no item filed for them |
| 3 Pyrelands main, run 1 (stale AshLadder) | 27 PASS / 3 FAIL / 6 UNMEASURED | see below |
| 3 Pyrelands main, run 2 (pruned, new world) | 25 PASS / 3 FAIL / 8 UNMEASURED: ground_deep_ash FAIL, ruins_scorched FAIL, scorchfruit_produces FAIL; scorchfruit_spoils_fast, furnacebeast_warmth, furnacebeast_heats_room, fulgurite_after_lightning, herd_follows UNMEASURED; all else PASS | |
| 3 long split | burn_line_present **PASS** (5 fires after 120360 ticks); fresh_burn_feeds_the_field **PASS** (bonus 0.498 after burn, field 0.4 -> 0.898); embergrass_regrows UNMEASURED CALIBRATING (day3 35.5%, day7 59.4%) | |

## New ash-build rows
ground_deep_ash **FAIL MOD** (0.840 of 57454 cells on world 1, 0.778 of 54676 on world 2, bar 0.85; PYRE_DEEP_ASH_TUNE_ONE_POINT_SHORT) ·
ash_fertile_when_watered PASS x2 · ash_drift_common PASS x2 (AshDrift 40.0 commonest) · ash_dusting PASS x2 · scorch_fruit_seed PASS x2 (fire_tick_effects) ·
ruins_scorched PASS (10/10) then **FAIL** (2/10) (MOD untraced; PYRE_RUINS_ASH_DIAGNOSE_TEN_THEN_TWO) · mapgen_log_clean PASS x2 · grass_chokes_ground PASS x2 ·
fresh_burn_feeds_the_field PASS.

## Non-PASS classes
- scorchfruit_fire_born: FAIL in run 1 (cap 40 already holding 35 fruit from the earlier fire_tick_effects chain, HARNESS), 25 fruit alone, PASS in run 2. PYRE_HARNESS_SCORCH_CAP_REPAIR_SHARED_BUDGET.
- scorchfruit_produces: FAIL run 1 and run 2 (no yield after forced harvest); alone: harvest worked, ingest FAIL once (window 1500), PASS once (1200). Untraced MOD/HARNESS. PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST.
- scorchfruit_spoils_fast run 2: UNMEASURED (stack vanished before its timer). furnacebeast_heats_room run 2: UNMEASURED SITE (control room 48 C, never under 24 C). furnacebeast_warmth, fulgurite, herd_follows: unchanged (no tool / no drive).
- burrowers_dive PASS both runs (pass 5's flake did not recur).
- Selftests: run_selftests 411/414, **FAIL selftest_settings_screens** (Pyrelands 13 groups, test expects 12; PYRE_SETTINGS_SELFTEST_FIX_UNLUCKY_THIRTEEN). 2 skipped.
- DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER filed (the AshLadder.xml leftover).

## Player.log (tier) vs pass 5
Lines with "error": pass 5 = 19 (12 were `burnedDef is flammable` on the retired rungs); pass 6 after pruning = 7, all pre-existing RUT_Jawa weapon-money and vanilla meme config errors; `burnedDef is flammable` 0. NRE 0, Exception 0, FaceAdjustmentDef 0.
Before pruning pass 6 had the one extra "XML error: Could not register node RM_FE_AshBase" (above).

## Section H exit criterion (design/RimMandrake/ratchet_workflow_and_token_burst_design_2026-10-11.md)
1. proof_all 0 FAIL 0 UNMEASURED: **MET** (106/106 at 7589d73ef6).
2. validation_v2 0/0: **MET** (61/61). River extension 0 FAIL: **MET**; its 3 UNMEASURED are SITE-presumed but have **no filed item**, so the "only if SITE with a filed item" clause is **UNMET**.
3. Pyrelands 0 FAIL 0 UNMEASURED: **UNMET** (3 FAIL, 6 UNMEASURED run 2). `modcheck floor --all` shows Pyrelands VALIDATED, 21/21 bars covered, "bar met".
4. BENCH pilot items done/superseded: **UNMET** (PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED built with A1 FAIL, A4/A5 partial; ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR, PYRELANDS_* and the four items filed today open).
5. selftests N/N and code_review CLEAN: **UNMET** (411/414; 9 C# files of the ash build DIRTY, 3 never reviewed: PyrelandsAshField.cs, PyrelandsFuzz.cs, FlowWorksIrrigationRead.cs).
6. Owner review queue provenance: not checked (owner line, out of scope).

PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED NOT closed (A1 FAIL). `rimflow verify` recorded per criterion: A1 fail, A2 pass, A3 pass, A4 partial, A5 partial.
