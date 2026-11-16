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
- **Waiting on:** the fixer on RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS; his card on ugliness_visible's wording (RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS); then blind cycle 2
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
