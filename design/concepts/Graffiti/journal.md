# Graffiti: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to.

Graffiti entered the pipeline on the owner's word, outside the four-mod intake rule: "Graffiti should be properly
entered into the pipeline as usual including a first touch Designer." (OWNER, item
RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED, 2026-11-15T04:53:51Z). `maturation_dispatch.json` lists
it among the advancing mods; the Dispatch step never launches the Designer.

## The mod as it stands

- **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 2:37 PM PST (`version/stage_record.json`).
- **Design Version:** none yet; it is cut at the Designer's Lock step, which Graffiti has not passed.
- **Designer:** `stage.json` reads its Lock step, status waiting_owner, parked (second_refusal, 2026-11-15T09:32Z) on
  `park_summary.md`. Accepted: Read, Argue the idea, Argue the edge, Write, Exam (64 frozen scenarios, both Readers
  matched). The coverage judge (rm-coverage-judge-1794734941) holds 22 of 24 fixes; gaps g1 (after_the_raid shares
  inv_player_orders with the spree corridor) and g18 (a wall's far side takes paint, no live control) stay open. The
  Designer can fix both at its Write step without him.
- **Waiting on:** the fixer on RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS; then blind cycle 2 (his card on ugliness_visible's wording is answered and carried out, 2026-11-16 8:23 PM PST)
- **Budget:** 6.94M weighted tokens of the 4M task cap spent (advisory outside a judge loop); the judge-and-rework loop
  since 2026-11-15T08:27Z has spent about 3.4M of its 8M ceiling (twice the cap).
- **Next:** on his word, the Designer (`role_launch.py`) reopens; rework sends it to the Write step for g1 and g18.
- **Open questions for him:** the park question above. His recorded answers: root plus raiders who leave threats and
  marks; agent walks first; face (B) the spree corridor; a standing raider mark makes that faction's next raid sooner
  or bigger, announced by a letter (the letter must name the wall mark as the cause:
  RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL).

## History (dated, added to only)

### 2026-11-14 9:00 PM PST, Stage 1 begins: the Designer's first touch

The owner filed the entry item at 8:53 PM PST; the first Designer run (rm-role-designer-1794718558) opened at 9:00 PM
PST. Answers to its asks came by card between 9:43 PM and 11:36 PM PST (ledger notes on the item).

### 2026-11-15 5:40 AM PST, journal started and record seeded

Written by a Conductor helper (BENCH) answering "Are all the mods being advanced right now?": Graffiti had a Designer
record but no maturation record, so `maturation.py next Graffiti` read UNMEASURED. Seeded from this journal. Nothing
was launched: the park waits on his word.

### 2026-11-15 11:39 AM PST, version change: UNMEASURED to 0.1.0 (by BENCH)

- Why: VERSION.json locked as 0.1.0 on his card 2026-11-15 11:33 AM PST, Lock as 0.1.0 now (OWNER:1794771556666342734)
- The UNMEASURED record (at Designer (Stage 1)) is kept as `version/stage_record_UNMEASURED.json`.
- Was, "Stage now": - **Stage now:** Stage 1, the Designer, since 2026-11-14 9:00 PM PST (`version/stage_record.json`).
- Record: `version/stage_record.json`.

### 2026-11-15 12:58 PM PST, Stage 2 preflight: scenes.json re-pinned (steward, BENCH)
- The preflight's lock-pin check refused `scenes.json`: commit `68f199064a` (11:58 AM, after the 11:33 lock) rewrote sc_wall_closeup's control from "expected fail until RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL lands" to the landed fix's concrete read (live row A9). His lock card named that defect as staying in 0.1.0, so this is test text following an in-version fix; no bar changed. Re-pinned in `version/bars.md` (was `31ef2c4933`, now `26cdc34d4b`); delegated call, steward.
- Preflight program: `version/pilot_throwaway/preflight_graffiti.py` (throwaway, no model), table from `version/pilot_throwaway/make_test_table.py`; record `version/preflight.json`.

### 2026-11-15 1:01 PM PST, stage change: Preflight (Stage 2) to Offline build (Stage 3) (by BENCH)

- Why: delegated: steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, Stage 2 preflight run and read
- Checks passed: order, by, version, hold, preflight_record, steward_confirms.
- Steward confirms: Read version/preflight.json (preflight_graffiti.py, 19 checks, planted run 19/19 red, verdict refuse, 3 refusals, all in built offline test ship_check.py): art clause blind to the vanilla AssetBundle texture UI/Designators/RemovePaint and settings clause stale (6 fields/'Sacred Marks' vs the shipped 8/'Feelings while near a mark'), both a broken checker criterion filed RIMMANDRAKE_MEND_GRAFFITI_SHIPCHECK_STALE_LABEL_BLIND_BUNDLE; 37 files not CLEAN, Stage 3 review work filed RIMMANDRAKE_REVIEW_GRAFFITI_SOURCE_THIRTY_SEVEN_FILES_DIRTY. None is a spec fault. The one Stage 1 refusal (scenes.json blob drift from 68f199064a, sc_wall_closeup control text following the in-version A9 fix) was re-pinned in version/bars.md with a journal line. Owed tests (3 offline, 1 live, 20 absent scene entries) are Stage 3 work per the lock rule.
- Was, "Stage now": - **Stage now:** Stage 2, preflight, since 2026-11-15 11:39 AM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** his own word (words or a card) on RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED: rework, certify as it stands, waive a gap, or stop. A seat note or a --per-ruling act does not lift the park (`designer_stage.standing_park`).
- Record: `version/stage_record.json`.

### 2026-11-16 1:37 PM PST, stage change: Offline build (Stage 3) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: delegated: steward run RIMMANDRAKE_ADVANCE_GRAFFITI_PAST_OFFLINE_BUILD, every Stage 3 exit test passes
- Checks passed: order, by, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate.
- Steward confirms: Read maturation.py next (exit tests order, version, hold, every_bar_has_a_check_that_runs, table_version, fourth_cycle, judge_certificate all pass; no not-met reason to sort, so no RECORD GAP/CRITERION FLAW/REAL MISS), certificate OK (6 bars' offline deciders registered, run on this build, green; red_seen UNPROVEN warning only, tracked by RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN), gate OPEN. No blind cycle yet, so no tests_edited.json to judge. Open carry-forward: T_SHIP_CHECK (stage 4-5 test, FAIL rc1 2026-11-16 21:22Z: deploy drift plus the clauses in RIMMANDRAKE_MEND_GRAFFITI_SHIPCHECK_STALE_LABEL_BLIND_BUNDLE) and RIMMANDRAKE_REVIEW_GRAFFITI_SOURCE_THIRTY_SEVEN_FILES_DIRTY (Stage 3 Output 'review status clean', not an exit criterion); both stay open for the blind challenge. Verdict: advance.
- Blind cycle 1 of this visit (1 in all).
- Was, "Stage now": - **Stage now:** Stage 3, offline build, since 2026-11-15 1:01 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-15 1:01 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 2:37 PM PST, stage change: Blind challenge, tests first (Stages 4 and 5) to Blind challenge, tests first (Stages 4 and 5) (by BENCH)

- Why: steward road back from blind cycle 1 (exit not met): raider pressure unbuilt (REAL MISS) refiled as RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS for a fixer; ugliness_visible's wording waits on his card (RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS); the zero-offline-bar block was a reader flaw, fixed (RIMMANDRAKE_PASS_BLIND_EXIT_ZERO_OFFLINE_BARS_GRAFFITI_STUCK)
- Checks passed: order, by, version, hold, fourth_cycle, judge_certificate.
- Steward confirms: read cycle_1/SUMMARY.md, faults.json, tests_edited.json ([], no test touched) and next's three reasons: exit_met false (consequence), no offline bar (CRITERION FLAW in maturation.py, fixed), 2 Problems open (raider pressure REAL MISS; ugliness CRITERION FLAW whose bar words are his card). Verdict: not met; cycle 2 opens after the fixer
- Blind cycle 2 of this visit (2 in all).
- Was, "Stage now": - **Stage now:** Stages 4 and 5, the blind challenge (tests first), since 2026-11-16 1:37 PM PST (`version/stage_record.json`).
- Was, "Waiting on": - **Waiting on:** not yet written for this stage; the steward writes it (the earlier line is in the history entry of 2026-11-16 1:37 PM PST).
- Record: `version/stage_record.json`.

### 2026-11-16 8:55 PM PST, ugliness_visible reworded on his card (re-pin)

Owner, by card 8:23 PM PST: "How should the ugliness bar read?" → "Look and stat agree" (OWNER:1794889675303725702). The
tree leaf, `sc_beauty_pair`'s control and the north-star line `mark_ugliness_is_visible` now say a vandal scrawl looks
worse than a tally and inspects as uglier when the same hand made both, with no stat value named; the north star was
re-validated on that card (`modcheck validate`, hash 46b0a808a4). The code the card said it costs: a scrawl's beauty is its
craft less `RM_GraffitiKernel.ScrawlVandalism` (`MarkBeauty`), so a same-hand scrawl inspects uglier at every craft; before
it they tied for an awful or a poor hand. New offline decider `T_UGLINESS_OFFLINE`
(`src/RimMandrake/Utils/selftest_graffiti_ugliness.py`, red on the old formula at awful and poor); the live half of
`sc_beauty_pair` (`validation.py beauty_pair`, `RM_GraffitiStage.Pair`) is UNRUN. `bars.md` re-pins tree.json and
scenes.json. Item RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS.

### 2026-11-17 6:52 AM PST, four oracles to be reworded as experiences; the change waits for blind cycle 2 (Conductor helper)

The owner's ruling of 2026-11-16 (a passing bar is an experience, never a tuning number; `design/RimMandrake/standing_rulings.md`)
and the Conductor's brief of 2026-11-17 reword four Designer oracles that pin numbers he never set: `marks_various` (3 defs,
5 def-variant pairs), `rereads_daily` (60000 ticks), `stories_not_tax` (plus or minus 3 mood) and `weathering_bounds_marks`
(the last 40 percent, alpha 1 before 60 percent). Each keeps its experience; the numbers stay in code as tuning. Blind
cycle 2 was live, so the edit and the re-pin are queued: `D:\ClaudeWork\rimmandrake\conductor\apply_card_rewords_20261117.py`,
item RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.

### Conductor interventions (one line each, added to only; the form is in the spec §5, "The steward and the journal")

- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 6:52 AM PST, kind hold): no advance past Stages 4 and 5 and no blind cycle 3 on Graffiti until the four rewordings (`marks_various`, `rereads_daily`, `stories_not_tax`, `weathering_bounds_marks`) have landed in tree.json and been re-pinned; blind cycle 2 (unit `rm-detached-bench-rimmandrake-judge-graffiti-blind-cycle-t-1794925227`) runs on to its end and is not stopped. Lift it with a later line of the same form, `kind release`, once the queued change has landed and re-pinned. Source: the Conductor's order in RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 9:26 AM PST, kind re-pin): the four rewordings (`marks_various`, `rereads_daily`, `stories_not_tax`, `weathering_bounds_marks`) landed in tree.json, scenes.json (`sc_spree_variety`) and sheet.md (d1542a3675); `designer_stage.py repin` re-pinned stages 2, 3 and 5 (7e59c0c1ba; 68f199064a tied to his lock card by route (a) of RIMMANDRAKE_TIE_GRAFFITI_REPIN_TEST_TEXT_COMMIT_NO_CARD); stage 4's exam is void and the concept is unlocked for its retake (RIMMANDRAKE_UNLOCK_REPIN_VOIDED_EXAM_NEXT_OPEN_REFUSED, d2a3509a53), so the maturation chain retakes the Cold Reader exam and gives ONE coverage-judge look before anything else. Source: OWNER:1794842055508243067.
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-17 9:26 AM PST, kind release): blind cycle 2 (unit `rm-detached-bench-rimmandrake-judge-graffiti-blind-cycle-t-1794925227`) has ended (exit not met, 2 Problems fixed at dad3e902ac) and the four rewordings have landed and been re-pinned; the hold of 6:52 AM PST is lifted. Source: the Conductor's order in RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS (item RIMMANDRAKE_APPLY_BARS_CARD_PATCH_WHEN_BLIND_JUDGES_END).
- STEWARD (stage 4+5, 2026-11-17 9:55 AM PST, RIMMANDRAKE_RETAKE_GRAFFITI_EXAM_AFTER_LOCKED_CHANGE, chain): re-pin of 9:10 AM confirmed (tree e6507f3b, sheet 26a15750). Cold Reader exam retaken in full: 46 scenarios (36 examiner, 10 challenger), frozen 4be2a731; two Readers 46/46, accept_where_reject_core 0, no challenger miss; control on `going_over` missed e12, e13. ONE coverage look (rm-coverage-judge-1794936862): not_covered, 2 gaps, both REAL MISS (scenes not reworded with their oracles, criterion sound): g1 `sc_spree_variety` (RIMMANDRAKE_MEND_GRAFFITI_VARIETY_SCENE_JUDGE_SEES_NO_CAPTURE), g2 `sc_lived_in_soak` (RIMMANDRAKE_MEND_GRAFFITI_SOAK_SCENE_SUM_HIDES_TAXED_PAWN). Judging stopped; the next look is his word.
- STEWARD (stage 4+5, 2026-11-18 10:13 AM PST, RIMMANDRAKE_RETAKE_GRAFFITI_EXAM_AFTER_LOCKED_CHANGE_RUN_TWO, chain): re-pin of 9:58 AM confirmed (stages 3 and 4 for scenes only; tree e6507f3b and sheet 26a15750 unchanged, `stale_inputs` empty). Exam not retaken: the 2026-11-17 exam (122/122, control on `going_over`) passes its gate on that same tree and sheet, which are all its Readers see (delegated; the chain brief now says so itself, RIMMANDRAKE_SPARE_EXAM_RETAKE_WHEN_ONLY_SCENES_MOVED, 98912ff77c). His grant of 2026-11-17 applied as the final look (after item closed, 6c7d175b52 on origin/main; fix claim g1 in `coverage_fixes.json`): rm-coverage-judge-1795025027 read **covered, 0 gaps**, g1 `stories_not_tax` fixed. Not signed: the coverage brief reads UNTESTED, so the verdict is advisory and judging waits for RIMMANDRAKE_RECALIBRATE_COVERAGE_BRIEF_UNTESTED_SINCE_LAST_EDIT.
- CONDUCTOR INTERVENED (stage 3, 2026-11-18 10:22 AM PST, kind hold): the Dispatch tick launches no steward, fixer, re-pin, exam retake, blind cycle, coverage look or visit on Graffiti until the Wednesday 2026-11-18 token resets (the last, lukas, about 3:00 PM PST). Owner, 2026-11-18 10:20 AM PST: "Stop that Graffiti work. Unauthorized item until the token reset." Unit `rm-detached-bench-rimmandrake-route-graffiti-cycle-two-fai-1795025961` was stopped at 10:22 AM; the retake `rm-detached-bench-rimmandrake-retake-graffiti-exam-after-l-1795024763` had already ended. Release after the resets (item `RIMMANDRAKE_REPIN_GRAFFITI_SOAK_FIX_AFTER_WEDNESDAY_RESETS`).
- CONDUCTOR INTERVENED (stage 4+5, 2026-11-18 10:22 AM PST, kind hold): the Dispatch tick launches no steward, fixer, re-pin, exam retake, blind cycle, coverage look or visit on Graffiti until the Wednesday 2026-11-18 token resets (the last, lukas, about 3:00 PM PST). Owner, 2026-11-18 10:20 AM PST: "Stop that Graffiti work. Unauthorized item until the token reset." Unit `rm-detached-bench-rimmandrake-route-graffiti-cycle-two-fai-1795025961` was stopped at 10:22 AM; the retake `rm-detached-bench-rimmandrake-retake-graffiti-exam-after-l-1795024763` had already ended. Release after the resets (item `RIMMANDRAKE_REPIN_GRAFFITI_SOAK_FIX_AFTER_WEDNESDAY_RESETS`).
- CONDUCTOR INTERVENED (stage 6, 2026-11-18 10:22 AM PST, kind hold): the Dispatch tick launches no steward, fixer, re-pin, exam retake, blind cycle, coverage look or visit on Graffiti until the Wednesday 2026-11-18 token resets (the last, lukas, about 3:00 PM PST). Owner, 2026-11-18 10:20 AM PST: "Stop that Graffiti work. Unauthorized item until the token reset." Unit `rm-detached-bench-rimmandrake-route-graffiti-cycle-two-fai-1795025961` was stopped at 10:22 AM; the retake `rm-detached-bench-rimmandrake-retake-graffiti-exam-after-l-1795024763` had already ended. Release after the resets (item `RIMMANDRAKE_REPIN_GRAFFITI_SOAK_FIX_AFTER_WEDNESDAY_RESETS`).
