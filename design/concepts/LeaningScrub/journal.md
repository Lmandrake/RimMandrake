# LeaningScrub: journal

This is the mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. The
**history** below it is only ever added to.

LeaningScrub entered the pipeline on the owner's word: "Could we do steps 1 and 2 using GPT for the remaining Biomes? That
would be a LOT of user interaction that I could help with today too." (OWNER, 2026-11-15 ~4:30 PM PST), with his
correction "I think we DO want a Designer that can run on CODEX." (~4:40 PM PST). Item
RIMMANDRAKE_ADMIT_LEANINGSCRUB_DESIGNER_ON_CODEX_FIRST_PROOF.

## The mod as it stands

- **Waiting on:** the Designer's first-touch run, on Codex (the Dispatcher's DesignerCodex lane; stage.json `runner: codex`).
- **Stage now:** Stage 1, the Designer, since 2026-11-15 5:30 PM PST (`version/stage_record.json`).
- **Mod:** `src/RimMandrake/LeaningScrub`, the RM_LeaningScrub biome.
- **Design Version:** none yet; the pipeline locks a new mod at 0.1.0 when the Designer pass is done.
- **Ceiling:** Stage 2 (Preflight). Not on `maturation_dispatch.json` `advancing`: no builder launches on it.
- **Input:** a Codex first-touch draft, to verify, never to copy: `D:\ClaudeWork\rimmandrake\codex_designer_drafts_20261115\LeaningScrub.designer_draft.md` (stage.json `draft_input`).

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
