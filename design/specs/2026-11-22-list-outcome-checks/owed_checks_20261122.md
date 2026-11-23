# The Conductor's owed list, given outcome checks: 2026-11-22, about 11:40 PM PST

Input: `rimflow queue CONDUCTOR --owed --all`, read at about 11:00 PM PST: 42 items (35 actionable, 7 waiting).
Item: `RIMMANDRAKE_BUILD_LIST_OUTCOME_CHECKS_SEVEN_DONE_NEVER_CLOSED`. Each check is on its item's ledger (`effect` event).

| count | what |
|---|---|
| 0 | closed by the list_effect tick. No open item on the list had a check that already passed: the census's 7 "done, never closed" items (`design/specs/2026-11-22-one-view-of-open-work/census.md`) were all closed by hand before this run, and the one fresh case, `RIMMANDRAKE_RESUME_PLAN_RUN_WITH_HIS_SECOND_PIPELINE_DIRECTION`, was closed by its own run at 11:04 PM PST, before its check could be attached. |
| 4 | now carry a check that fails (each seen failing at attach) |
| 1 | closed already by its own run (above) |
| 37 | cannot carry a check now, for four reasons (below) |

## The 4 checks

- `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`: every "Not ruled yet" line of
  `design/specs/2026-11-21-guiding-principles/conversion_list.md` reads "none" (one row is left: `pyrelandsEnabled`).
- `RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS`: the tag `mod/GimmeSomeSlack/v0.1.1` exists.
- `RIMMANDRAKE_WORK_NIGHT_POINTERS_OF_NOV_TWENTY_SWITCH_HANDOFF`: its three pointers' items are closed
  (`RIMMANDRAKE_REFUSE_STAGE_THREE_BAR_READS_NO_BUILT_FILE`, `RIMMANDRAKE_RUN_TARGETED_CHECKS_PAST_UNBUILT_MUST_SHOW_LINES`,
  `RIMMANDRAKE_ADMIT_MACHINE_LOOKS_MOD_WITH_FRIDGE_AND_BATTERY`).
- `RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT`: the items of batches 6 to 17 of
  `design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md` are closed (none is filed yet).

## The 37 that cannot carry one, by reason

- **15: done means he was told, or he acted** (a page, a card, a look, a pick, a go, a hold lift). A program cannot
  see that he read or decided: `REPORT_CLEAN_SHARE_HISTORY_TREEMAP_WAS_ALL_GREEN`, `REPORT_DAILY_FILED_COUNT_AFTER_FILING_GATE_STARTS`,
  `BRING_HIM_THE_CLEAN_HOUSE_ADVICE_AND_BOTH_CODEX_STUDIES`, `SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST`,
  `WEIGH_DROIDWORKS_SOON_SO_DROIDS_JOIN_EVERY_MOD_TEST`, `STUDY_WHAT_ONE_WEEK_OF_MODS_TAUGHT_ON_NOV_TWENTY_NINE`,
  `TELL_HIM_ROT_SPORE_MUSHROOM_PERFORMANCE_VERDICT_HIS_HUNCH`, `CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED`,
  `EVAL_CRYSTALLIZE_SKILL_ONCE_AFTER_EDITS_SETTLE`, `RELEASE_CONTAGION_JUDGE_ONE_LOOK_HIS_WORD_GIVEN`,
  `DEPLOY_THIN_OUTLINE_ULLAI_INSTALLED_BUT_NO_GAME_HAS_IT`, `READ_STEVE_RESUME_REPORT_CAN_FILL_RAISE_NOISE`,
  `ADD_COVER_FADE_STATION_TO_NEXT_FLOWWORKS_LOOK_HE_JUDGES_IT`, `GENERATE_SCRAPPER_JETTY_HEAVY_BRIDGE_ART_DEFAULT_LOOK_SHOWS_OLD`,
  `READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO`.
- **9: a decision or judgement with more than one right outcome**, or a bundle too wide for one check (it needs the
  Shape split first): `BUILD_CODEX_BUILDER_LANE_WHILE_CLAUDE_RUNS_DRY`, `DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX`,
  `DECIDE_TWELVE_RULE_CONFLICTS_THE_COMPRESSION_LISTED`, `COLLECT_REWRITE_CONFLICTS_UNDEFINED_TERMS_ONE_LIST`,
  `FIX_FILED_PIPELINE_TICKETS_AFTER_WEDNESDAY_RESET`, `ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION`,
  `SETTLE_FOUR_ROWS_THE_NEEDS_TRIAGE_LEFT_TO_CONDUCTOR`, `WORK_EIGHTY_OWNER_TICKETS_AFTER_GATES_OPEN`,
  `CARRY_SUNDAY_SITTING_STATE_ACROSS_THE_WINDOW_RESTART`.
- **10: a part names no outcome a program can find yet** (read a result, launch a run whose item is not named, a
  folder that does not exist): `VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO`, `SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`,
  `READ_REVIEW_METHOD_RUNS_THEN_LAUNCH_SCAN`, `LAUNCH_TICKET_JUDGING_SLICES_WHEN_PLAN_LANDS`,
  `LAUNCH_RUN_CLONE_GROUP_AFTER_LIVE_RUNS_END`, `ROUTE_SLACK_VISIT_TWO_FAILURES_READ_LATE_RUNS`,
  `ASSIGN_LEFTOVER_CONTEXT_CHANGES_NEITHER_WORKER_HAD`, `LAUNCH_CODEX_REVIEWS_OF_MOD_CODE_AND_ART`,
  `CHECK_SCRATCH_QUEUE_SHRINKS_BEFORE_INCIDENT_CLOSES`, `ADD_FRIDGE_ART_TO_ELECTRICAL_RESKIN_HOME` (no Machine Looks
  concept folder exists, so its scope has no home to check).
- **3: the check needs an instrument or test that does not exist yet**: `RERUN_FAULT_WINDOW_VERDICTS_ON_CLEAN_BOOT`
  (code work with no acceptance test), `RECORD_FOURTEEN_OF_HIS_MESSAGES_THE_PROBE_FOUND_HOMELESS` (the probe counts a
  home only within 72 h of the message, so it cannot see a late record), `REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE`
  (the art judge's verdict is in no record a program reads).

All names above drop their `RIMMANDRAKE_` prefix. The sort is one agent's reading of each item's title and notes
`[guess ~80% per item]`; a fresh reader was not run.
