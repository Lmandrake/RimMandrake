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
