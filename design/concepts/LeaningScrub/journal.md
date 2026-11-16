# LeaningScrub: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

LeaningScrub entered the pipeline on the owner's word: "Could we do steps 1 and 2 using GPT for the remaining Biomes? That
would be a LOT of user interaction that I could help with today too." (OWNER, 2026-11-15 ~4:30 PM PST), with his
correction "I think we DO want a Designer that can run on CODEX." (~4:40 PM PST). Item
RIMMANDRAKE_ADMIT_LEANINGSCRUB_DESIGNER_ON_CODEX_FIRST_PROOF.

## The mod as it stands

- **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 9:21 AM PST).
- **Stage now:** Stage 3, offline build, since 2026-11-16 9:21 AM PST (`version/stage_record.json`).
- **Current work:** Designer Stage 3 rework completed against OWNER:1794835478275153823, pending launcher acceptance of this run's result. Gate A, scenes/floor and showcase structure pass; no implementation or play is certified.
- **Next:** fresh Stage 4 exam of the rewritten artifacts, then coverage/Lock. Prior exam is historical. Owner first-touch certification remains owed.
- **Mod:** src/RimMandrake/LeaningScrub, the RM_LeaningScrub biome in the composed package. No Design Version is locked or handed off.
- **Current bar:** six validated families; sweetline healing included, technology and calling-pyre next version, settings/reload universal floor, no legacy save preservation.
- **Open criterion work:** g12 with the neutral fixer. g1–g11 have design correction claims. The UNTESTED judge verdict stays advisory; unchecked=[].
- **Live look:** existing home/routes/ordered-expedition offer remains unexecuted. Designer holds no bridge and makes no game/restart/deploy action.

## History

- 2026-11-15, BENCH: ranked 3rd of 25 biome mods by measurement (review clean 85/129, testq 3/5 jobs done with 49 PASS
  and 0 FAIL rows, selftests 10/10 green; `D:\ClaudeWork\rimmandrake\conductor\next_biome_mod_20261115.md`). Seeded at
  the Designer (`designer_stage.py init --runner codex --draft`, `maturation.py seed`).

## Stage 3 — rm-role-designercodex-1794799806

Wrote sheet/tree/plan/scenes/floor and supporting source/setting/audit contracts. Gate A, showcase set and stage check pass; result.json is done for this run only.70 leaves,81 planned scenes,7 showcases and7 remainder checks cover71 required units; two absent cuts retain an explicit check. Five proof-contract build items filed without queue priority. No live acceptance, exam, signature or lock inferred. No bridge, game, restart, deployment, mod-code or art action. See write_checks_03.json and record.stage_3. Launcher alone closes/advances the stage.

## Stage 3 retry — rm-role-designercodex-1794806809

The launcher rejected the previous result with 20 reported root-reference errors. The earlier local check passed, and the launcher rejection remains the recorded outcome for that attempt.

This retry checked each reported leaf/root pair against BENCH and Dispatcher. Both checkouts now expose the same eight DRAFT observations at north-star hash 787d3f37799dd51480095df641fcbb8fa8c2c8c9c0083fd261b8b0a666c377e5. All 70 leaves resolve, and each checkout rejects an intentionally missing root. Full result validation passes against both. All 95 primary source hashes match the previous source audit.

Gate A passes, the showcase set is accepted, and designer_stage.py check reports that this run's result.json would be accepted. The existing design remains the submitted Stage 3 product. Current gameplay acceptance, exam, signature and owner first-touch certification remain pending. Per-rejection evidence is in write_checks_03.json. The launcher owns stage closure.

## Stage 4 — rm-role-designercodex-1794815494

The frozen tree and sheet passed the independent Claude Opus exam, 18/18 with zero core false accepts. Six Challenger cases joined twelve Examiner cases before freezing. Two fresh Readers and a fresh Control received only their allowed documents and scenario text. The Control missed the non-raid-weight case after removal of raid_weight and its rule. Raw JSON, session UUIDs, briefs, frozen scenarios and per-reader verdicts are retained under exam_runs. All five helpers were charged580949 weighted tokens, exceeding the500000 run allowance by80949. The task cap retains budget.

Fresh Claude CLI UUID identities exposed an unsupported identity format in the validator. Filed RIMMANDRAKE_ACCEPT_EXAM_SESSIONS_UUIDS_ARE_IDENTITIES, observed two regression failures, and repaired the identity parser with all stage selftests passing. Exam criteria and identity-reuse rejection remain enforced. Live acceptance, coverage, owner first-touch and Lock remain pending. Launcher alone closes and advances this run.

## Stage 2 owner answer — rm-role-designercodex-1794838582

Read OWNER:1794835478275153823 and answered a_root_validation_2 with its exact amendments. Preserved delegated sentence approval. Corrected canonical bar for owner validation before Stage 3 rework; retained all twelve advisory gaps and unchecked=[]. Next-version technology and calling-pyre filed. Settings/current-schema reload remain floor duties, save preservation is out, and sweetline healing is a new explicit obligation. No derived artifact, game or bridge action. Launcher alone closes/advances.

## Stage 3 rework — rm-role-designercodex-1794840775

Bound the official tree to the corrected validated canonical root, preserving delegated sentence and first-showing provenance. Rewrote all derived scope, filed sweetline health and full advisory corrections in the existing five proof/product items, and retained next-version built characterization/removal checks. Catalog: 64 leaves including three instruments and one walk; 82 planned scenes (71 acceptance, five interactions, six explorations); six showcases plus eleven remainder checks account for all 72 required inventory units. All 23 floor lines remain applicable, with no exception. coverage_fixes.json claims g1–g11 and retains g12 routing; original twelve gaps and unchecked=[] are untouched. New exam, signature, actual play and owner certification remain pending. See write_checks_03_rework.json and source_audit_03_rework.json. result.json is for this run only; the launcher alone advances it.

## Stage 4 fresh exam — rm-role-designercodex-1794843033

The corrected validated six-family tree/sheet passed the independent Claude Opus Cold Reader exam: 18/18, zero core false accepts. Twelve fresh Examiner scenarios and six Challenger scenarios were frozen before either Reader. Both full Readers matched every case. The program-created control removed raid_weight and every statement of its rule; the Control accepted the non-raid spillover case that the full Readers rejected. Five actual session UUIDs, exact prompts, raw JSON, parsed verdicts, hashes and charges are retained in design/concepts/LeaningScrub/exam_runs/rm-role-designercodex-1794843033. Helpers consumed 468259 weighted tokens, fully charged. The prior exam/control are archived there as historical evidence. No main design inputs changed; delegated approval, corrected owner bar, advisory gaps and neutral g12 routing are preserved. This is a contract readability exam only. Live acceptance, coverage signature, owner first-touch certification and Lock remain pending. The launcher alone closes/advances.

### 2026-11-16 9:00 AM PST, version change: UNMEASURED to 0.1.0 (by BENCH)

- Why: delegated: steward: the stage record was seeded 2026-11-15 before the 0.1.0 lock and reads version UNMEASURED; opening 0.1.0 (VERSION.json, locked 2026-11-16 by the pipeline per RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME); first version of a new mod, no ordering contest
- The UNMEASURED record (at Designer (Stage 1)) is kept as `version/stage_record_UNMEASURED.json`.
- Was, "Stage now": none
- Record: `version/stage_record.json`.

### 2026-11-16 9:21 AM PST, stage change: Preflight (Stage 2) to Offline build (Stage 3) (by BENCH)

- Why: delegated: steward: Stage 2 preflight run (design/concepts/LeaningScrub/version/pilot_throwaway/preflight_leaningscrub_stage2.py, 18 checks, 10.7 s, verdict refuse with 1 refusal); planted-fault run refused 18 of 18
- Checks passed: order, by, version, hold, preflight_record, steward_confirms.
- Steward confirms: Read version/preflight.json (18 checks: 17 pass, C16 refuse 1), test_table.json (123 bars = locked_bars.json, every bar with a decider, pairs read from coverage_verdict parts and scenes.json requirement/exercises/coverage_rest; 82 scene entries, 81 absent = Stage 3 work under SCRUB_PROVE_*), bars.md (9 locked files, every blob equal at lock commit 06e9b621f6), the held row (owner_look_defects_2026-11-12 row 26 placed on biome_cast). The one refusal, C16 T_WILDLIFE_ZERO_PATHS row Z5 (RM_PyrelandsGiants.cs changed since review), is offline-build work (re-read and re-pin), filed RIMMANDRAKE_REREAD_SCRUB_PINS_AFTER_PYRELANDS_GIANTS_MOVED; not a spec fault. 10 game reasons (exploration/interaction scenes) were written by the table maker from each scene's kind, marked why_game_by, for the Stage 4 challenger to judge.
- Was, "Stage now": - **Stage now:** Stage 2, preflight, since 2026-11-16 9:00 AM PST (`version/stage_record.json`).
- Was, "Waiting on": none
- Record: `version/stage_record.json`.

### 2026-11-16 9:52 AM PST, offline build: four scene entries (by BENCH)

- RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_BARS_LEFT wrote `scene_arm_food`, `scene_arm_regrowth`, `scene_bloom` and `scene_cuts` in `src/RimMandrake/LeaningScrub/validation.py` (each with designer_stage scene-begin, a recovery save reloaded in finally, and its controls), proved against the fake game in `selftest_leaningscrub.py` (138/138 healthy, 17 new breaks each red on its own component), all UNRUN in game until Stage 6; bars not runnable 123 to 115. `sc_acoustic_payload` and `sc_native_cast` are not written: see the item's LEFT OPEN note.

### 2026-11-16 10:10 AM PST, offline build: ten scene entries (by BENCH)

- RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_LEFT wrote `scene_native_cast`, `scene_pyre_beliefs`, `scene_pyre_ritual`, `scene_acoustic_payload`, `scene_concealment`, `scene_cane_fuel`, `scene_colony_walk`, `scene_floor_runtime`, `scene_settings` and `scene_floor_persistence` in `src/RimMandrake/LeaningScrub/validation.py`, each with a pure checker the scene also shows refusing injected readings; watched red against the fake game before its behaviour was modelled, then green in `selftest_leaningscrub.py` (180/180 healthy, 147 breaks each red on its own component). All UNRUN in game until Stage 6. The settings census found `shirrelGlideEnabled` missing from the suite's DEFAULTS (added from the source). Dead cane's premium credit and heat bonus are not built in C# (`RM_DeadVenomvine_Fuel.xml` only admits it to the wood filter), so `sc_cane_fuel` is expected red at Stage 6. Bars not runnable 115 -> 104.

### 2026-11-16 10:47 AM PST, offline build: six scene entries (by BENCH)

- RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_BARS_LEFT wrote `scene_crown`, `scene_cruststar`, `scene_creep`, `scene_removed_save_preservation`, `scene_floor_payload` and `scene_floor_recovery` in `src/RimMandrake/LeaningScrub/validation.py`, each with a pure checker the scene also shows refusing injected readings; watched red against the fake game before its behaviour was modelled (27 components not PASS), then green in `selftest_leaningscrub.py` (211/211 healthy, 163 breaks each red on its own component). All UNRUN in game until Stage 6; `sc_crown` launches flyers and runs only with the owner present. Expected red at Stage 6: `sc_cruststar` (grazing is not built in C#), `sc_removed_save_preservation` (the RM_DefAliasDef aliases and the hidden `RM_Faction_CombHolds` still ship), `floor_payload` text (`RM_SweetlineWool` still promises bark-wardens: RIMMANDRAKE_STRIP_SCRUB_TEXT_WARDENS_CUT_BUT_STILL_SLEEPING). The floor_recovery probe found `_setting` restoring DEFAULTS instead of the captured value; it now restores the value it found. Not driven live (in the scene docstrings): an Explosive Growth soak pass, a smothered emitter, a sown neighbour. A fresh Opus review (9 findings) was folded in: vanilla's "Mature." inspect line read as full growth, creep controls counted map-wide and UNMEASURED until the on arm reaches the test emitters, crown arrivals ordered, no owner hold for a crown scene that never ran, the recovery restore unguarded and a restored-but-open recovery refused, Source/Kernel scanned, and the log window judged only between its own sentinels (drain_log keeps no cursor); `_setting` warns when it captures an off-default value. Still open from it: the creep guards are not read back after placing (a guard that failed to place reads as a taken cell, a false FAIL), and aliases added under Patches/ are not scanned. Bars not runnable 104 -> 95.

### 2026-11-16 11:42 AM PST, offline build: seven scene entries (by BENCH)

- RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_NINETY_FIVE_BARS_LEFT wrote `scene_fire_bias`, `scene_ix_fire_accountability` (owner_review hold), `scene_dripping`, `scene_felt_comfort`, `scene_home_routes`, `scene_ix_route_growth` (live, UNRUN in game until Stage 6) and `scene_economy_observer` (offline; `python3 src/RimMandrake/LeaningScrub/validation.py scene_economy_observer` runs it, 2 PASS) in `src/RimMandrake/LeaningScrub/validation.py`. Each keeps its verdict in a pure checker that a row shows refusing injected readings, and the observer was watched red under four mutations. `selftest_leaningscrub.py`: 239/239 healthy, 176 breaks each red on its own component (13 new). A fresh Opus review (12 findings) was folded in: fires lit at size 1.5 (vanilla spreads only above 1); the accountability field read alone; a sub-threshold unrelated fire; bystanders 9 cells off the fuel; route A's zone counted as storage; a walled site so A and B are the only corridors; geometry mirrored to the wind; research and invasion preconditions UNMEASURED when absent; harvester Plants 20; removed felt destroyed before the read; the observer given accrue, transfer and pay-debit events. Expected red at Stage 6: maker pursuit (no witness service in C#); developed-ground rows, because Walking's destination test (`RM_VenomvineForms.cs` Walk: no plant, no edifice, CanEverPlantAt) does not exclude zoned or roofed soil the way creep's NaturalFree does. Live UNMEASURED until an instrument exists: `sc_dripping`'s second harvest (no bridge tool sets an existing plant's growth in place; growDays 12) and its clean-start arm (`LSCRUB_DRIP_STARTUP`, a fresh launch). Bars not runnable 95 -> 86.

### 2026-11-16 12:12 PM PST, offline build: five scene entries (by BENCH)

- RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_EIGHTY_SIX_BARS_LEFT wrote `scene_gale_drawing` and `scene_fuzzviper` (owner_review hold), `scene_stamping`, `scene_maker` and `scene_floor_visual` in `src/RimMandrake/LeaningScrub/validation.py`, all live and UNRUN in game until Stage 6 (`bridge: src/RimMandrake/LeaningScrub/validation.py scene_<name>`); the selftest's fake game gained their behaviours and 18 breaks (268 components healthy, 194 breaks each red only where named). Bars not runnable 86 -> 78. Expected red at Stage 6: `stamping_base_binding` (no franchise-free stamper ships), `scene_maker` (the witness/trail kernel and shared evidence store are unbuilt), `scene_fuzzviper` (the run-wall ambush is a STUB). `scene_floor_visual`'s blind read and art-eval rows need a judge's files (`LSCRUB_BLIND_READ`, `LSCRUB_ART_EVAL`), and the Gale's isolated material-loader arms need a fixture hook that does not exist.

### 2026-11-16 1:20 PM PST, offline build: five scene entries (by BENCH)

- RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_SEVENTY_EIGHT_BARS_LEFT wrote `scene_gale_exposure`, `scene_working_wind`, `scene_raid_weight` (reads weights only, never fires a raid), `scene_hollow` (owner_review hold) and `scene_hoard` in `src/RimMandrake/LeaningScrub/validation.py`, all live and UNRUN in game until Stage 6 (`bridge: src/RimMandrake/LeaningScrub/validation.py scene_<name>`); the selftest's fake game gained their behaviours (307 components healthy, 220 breaks each red only where named). Bars not runnable 78 -> 70. Expected UNMEASURED at Stage 6 until a reader exists: `raid_weight_gale_only` and `raid_nonraid_unchanged` (no bridge tool reads `ChanceFactorNow`), `exposure_live_capacity_reduced` (`jawa/pawn_health` reports no Hearing/Talking level), `hollow_crawl_job` (the mod ships no crawl job). Both code files DIRTY until reviewed.
