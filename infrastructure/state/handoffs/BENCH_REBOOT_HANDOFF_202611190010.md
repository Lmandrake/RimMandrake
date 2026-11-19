# BENCH_REBOOT_HANDOFF_202611190010 — READ FIRST on wake

Follows `CONDUCTOR_HANDOFF_202611180743`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
He ruled (2026-11-18, cards and typed words on the ledger under `RIMMANDRAKE_REWRITE_BIOME_DESIGNS_UTINNI_LENS_SHIP_LEAVES_SOON` and `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING`) that every biome is designed as a short VISIT by the Jawa ship on the run from the Empire, never as a colony, and that **biome design work is done by Fable only** ("I don't trust Opus 5.5 with these sorts of things"). All 23 biomes now have a first-pass `design/concepts/<Biome>/design.md` and `rewrite_choices.md`; every first pass read some sources only in part, so **no old biome file is deleted until a second Fable reader marks the biome DELETE-READY and he has read the choices page.** Read one design yourself before pointing him at any (Greentide's is the format the rest follow).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Biome questions, by theme, in one sitting** (owed `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING`): cover, hull wear, fuel, scope moves against his earlier rulings (Abyss hidden ship into 0.1.0 against 2026-11-17; The Rot's giant into 0.1.0; Leaning Scrub's validated smother claim to later; Contagion's Sunbeam and Repulsor sold only by a 0.2.0 seller), locked Designer trees that describe colonies. His rulings so far: stop length is each biome's outer edge; partial orbit cover by biome; dark is MEASURED from the tidally locked map and hidden is separate; a sea floor is as concealed as the Abyss's Dark; **nowhere pauses the search indefinitely** (changes 2026-08-05; enact item `RIMMANDRAKE_ENACT_SEARCH_NEVER_PAUSES_SEA_FLOOR_VERY_CONCEALED`, not launched); every biome has slow biomass fuel, a few richer, one or two replete, buying fuel is the motive to trade; hull wear is in 0.1.0; "very Jawa" is a test for every solution; every biome must be uniquely worth visiting.
- **Judge order** (coverage judge before the Designer exam, `RIMMANDRAKE_REORDER_COVERAGE_BEFORE_EXAM_SIX_RETAKES_PAID`): explained to him at about 2:25 PM PST, not answered. A cheaper alternative was offered (re-run only the exam scenarios a refusal touched).
- **Delegated calls he can veto:** slot allocator finding 1 decided (b), a new account with no reading is unknown; the 2026-10-26 "never woken by a program" note removed on his word, run-end wake stays on.
- **Second-wave owner calls** (owed `RIMMANDRAKE_BRING_SECOND_WAVE_OWNER_CALLS_ON_ONE_CARD`): SteveDesktop swap, RMA or retire; when to re-ask Fable-from-start; phone-alert card; handoff cull age; row 14's ceiling release. Four mods sit paused at their stage ceiling; no release was taken or recommended this window.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. The Conductor's pointers each cite an open owed id too: file the act first (`rimflow file <ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; --check runs `owed.py check-pointers`. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS` — ledger lane (four tickets, all need splitting) launched 3:42 PM PST, running detached on Opus, cap raised; NEXT: read its run-end report and relaunch what it left open if the launcher did not (owed `RIMMANDRAKE_LAUNCH_UPGRADE_SECOND_WAVE_THIRTY_ONE_STILL_WAIT`)
- `RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK` — findings 2-5 landed e4f6ecd988; finding 1 decided (b) by the Conductor, note on the item; the launcher's own continuation is building it; NEXT: confirm the continuation closed it with a test seen red first (owed `RIMMANDRAKE_LAUNCH_UPGRADE_SECOND_WAVE_THIRTY_ONE_STILL_WAIT`)
- `RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE` — untouched this window; the coverage judge brief was calibrated today (7982ab44d2); NEXT: read the item and do its restamp step, or note why it still waits (this item is itself the owed id `RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE`)
- `RIMMANDRAKE_REWRITE_GREY_SEA_DESIGN_READ_IN_FULL` — one of four sea runs (Scald, Grey, Twilight, Chill) launched 4:00 PM PST on Fable, each writing its own design under design/concepts/TerminalBiomes/; NEXT: read the four reports and one sea design in full before telling him (owed `RIMMANDRAKE_VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO`)
- `RIMMANDRAKE_ROUTE_GRAFFITI_CYCLE_TWO_FAILURES_BACK` — Graffiti is HELD BY OWNER since 2026-11-18 ('Unauthorized item until the token reset'); its three runs were voided; NEXT: leave it until he lifts the hold; raise the lift at the theme sitting (owed `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING`)
- `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` — second run launched 3:20 PM PST for moves 1-3 and the deletions; first run measured 397 of 1,569 functions live and moved one module (25308a5645); NEXT: read its report; if a launch check went red, revert that landing first (owed `RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD`)
- `RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH` — fixer launched about 2:35 PM PST for the 19,204 /tmp/dc_* folders and their leaking selftest; still running at 4:20 PM; NEXT: when it ends, launch the reaping lane lane2_reaping.md (owed `RIMMANDRAKE_LAUNCH_TWO_RUNS_REFUSED_BY_FULL_POOL`)
- `RIMMANDRAKE_WAKE_CONDUCTOR_ON_RUN_END_LOG_ONLY_TODAY` — closed by lane C (d3bdf96d3b); this window only added his words removing the old schedule note (806d5fd303); NEXT: nothing to build; if a run-end wake holds a restart for more than a few minutes, file it (owed `RIMMANDRAKE_LAUNCH_UPGRADE_SECOND_WAVE_THIRTY_ONE_STILL_WAIT`)
- `RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD` — census of 377 old system tickets is on origin (design/RimMandrake/old_era_ticket_sweep_2026-11-18.md); the run was stopped by its cap and resumed at 3:30 PM PST with a larger one; NEXT: read its report and relaunch for the rows left (this item is itself the owed id `RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD`)
- `RIMMANDRAKE_VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO` — second readers running on Fable for the pilot three, BlueDesert to Slime, LanternDeeps to RustCathedral, TheSump to WeepingStones; NEXT: read each report's DELETE-READY line per biome and bring him the choices pages (owed `RIMMANDRAKE_VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO`)
- `RIMMANDRAKE_LAUNCH_TWO_RUNS_REFUSED_BY_FULL_POOL` — the clone pool was full at 16 of 16; the Sleeping Ice to Rot second reader and the builds lane resume were refused; NEXT: launch both with the commands in the item's title when `scratch_clone.py pool` shows a free clone (owed `RIMMANDRAKE_LAUNCH_TWO_RUNS_REFUSED_BY_FULL_POOL`)
- `RIMMANDRAKE_ENACT_SEARCH_NEVER_PAUSES_SEA_FLOOR_VERY_CONCEALED` — filed with its acceptance test, not launched; NEXT: launch it after the second readers end, so it edits settled designs (owed `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING`)

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `tail -F` on a file under /mnt/d delivers nothing; poll the line count instead (filed: lessons).
- A refused `rimflow file` (a 10-word name) is hidden by piping its output away; read its exit status or `rimflow show` before saying a debt is filed (filed: lessons).
- A multi-ticket lane on the default spend cap is stopped mid-lane; set `--budget-usd` for the whole job (filed: lessons).
- A run launched before e87491c5d0 ends with "no result JSON" and UNMEASURED spend: its report is lost, read its ticket's notes (see: `RIMMANDRAKE_MOVE_END_RECEIPT_OFF_RESULT_FILE_ROLES_FAILED`).

## Closed since the last handoff (148)

- `RIMMANDRAKE_ISOLATE_ITEM_NAMES_CASE_READ_LIVE_DISPATCH_DIR` — 22dfc868b5dd
- `RIMMANDRAKE_DESIGN_JUDGE_SAME_PROBLEM_MATCH_FOUR_ROUNDS_LOST` — 71a7fbc558e2286cabb595fa5a9c3807a8568135
- `RIMMANDRAKE_SPARE_EXAM_RETAKE_WHEN_ONLY_SCENES_MOVED` — 98912ff77c46
- `RIMMANDRAKE_RETAKE_GRAFFITI_EXAM_AFTER_LOCKED_CHANGE_RUN_TWO` — f8902b303d5d
- `RIMMANDRAKE_SYNC_MOD_TESTS_WITH_LANDED_RULES_BEFORE_JUDGING` — 6e1150d25b0c80ec75f31d06bbb8e854cd73e96a
- `RIMMANDRAKE_PASS_FRAME_LINE_TEN_PERCENT_FLOAT_SAID_FAIL` — 988f9fb5ac90
- `RIMMANDRAKE_KEEP_IN_FLIGHT_DEBRIS_OPEN_SWEEP_BURIED_IT` — c32e228e91ac
- `RIMMANDRAKE_REVIVE_REPLAY_BASE_SHA_GREEN_HID_THREE_UNRUN` — 2e1fc496155e
- `RIMMANDRAKE_VERIFY_REMOTE_LANDINGS_FOUR_SKIPPED_THE_DOOR` — bb1c21dc48
- `RIMMANDRAKE_SPLIT_UNREADABLE_LEDGER_FROM_FORGED_SOURCE_CITATION` — e1aabb027c20
- `RIMMANDRAKE_ALIGN_STAGE5_SCENE_CHECK_CLONE_READ_WRONG_TREE` — 37620ad3fcab
- `RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT` — 53a6f93f05889f97ae7a9b072a37b0955dd0a324
- `RIMMANDRAKE_FOLD_READER_CHARGES_INTO_JUDGE_PHANTOM_ROUNDS` — 53a6f93f05889f97ae7a9b072a37b0955dd0a324
- `RIMMANDRAKE_KEEP_REPAIR_BASELINE_THROUGH_FAILED_LOOK` — 53a6f93f05889f97ae7a9b072a37b0955dd0a324
- `RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED` — 55f15df7ab8a6b1e90fa49662dffacf0898cf7b3
- `RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT` — c3fdcceb5098
- `RIMMANDRAKE_SKIP_CHAIN_CAPPED_CONCEPTS_IN_DESIGNER_STALL` — 3595d573f3c4e9294dd8fcaa1d68f329670039b0
- `RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID` — 3043049714fe
- `RIMMANDRAKE_CHARGE_NOTHING_FOR_JUDGE_STOPPED_RUN` — 03e5975daf
- `VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT` — 00494512f965
- `RIMMANDRAKE_TRACE_DESIGNER_JUDGE_BLIND_TO_FILES_ON_DISK` — 45e3f2d4c7
- `SITESAVES_FIX_BACKUP_FILLS_REPO` — ff42dc4ac603
- `RIMMANDRAKE_MEND_THREE_RED_ROLE_SELFTEST_CHECKS` — ae4fbdb016
- `RIMMANDRAKE_REFUSE_MISSING_TOOL_SCENES_GRAFFITI_READS_READY` — 3a20b1745022160060d56b7bec94672bd2dc2db4
- `RIMMANDRAKE_REFUSE_HANDOFF_POINTER_WITHOUT_OWED_ID` — acadffc5b797
- `RIMMANDRAKE_NAME_NIGHTLY_SCOPE_TREE_CHECKS_COUNT_GREW_TWICE` — 0738f03bdd
- `RIMMANDRAKE_PRINT_JUDGE_COUNTS_WHEN_COVERAGE_CLOSES` — 28341732bb3f9511fc46b57189592dbabe40aaec
- `RIMMANDRAKE_ROUTE_SPENT_LIVE_FIXER_PILOT_BY_HAND` — 8c7fa18452
- `RIMMANDRAKE_LAND_DESIGNER_RUN_DONE_BUT_NEVER_HARVESTED` — 5d1e71e53d
- `RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS` — 3df65ba36203
- `RIMMANDRAKE_FIX_CONTROL_KILL_SURVIVOR_BOOKS_INIT_CODEX_CAUGHT` — c7c3b28e2b31
- `RIMMANDRAKE_EXPOSE_REFUSAL_RELEASE_VERB_CLEAR_UNREACHABLE` — 3136bb0d77d0
- `RIMMANDRAKE_WIDEN_FAMILY_TRIP_MARGIN_SUITE_ALMOST_RANG` — 93f3e5687e27
- `RIMMANDRAKE_ISOLATE_OWNER_HOLD_STALL_READER_FROM_CHAIN_TEST` — f2ce40bac8
- `RIMMANDRAKE_COUNT_REPAIR_PASSAGE_BLOCKS_FIFTH_MISSED_AT_CLOSE` — 7420c5bb76
- `RIMMANDRAKE_RUN_SELFTEST_MODES_AT_THE_DOOR` — 7c130159b2d4
- `RIMMANDRAKE_BOOK_FAILED_TICK_LAUNCHES_THREE_FALSE_HANDS` — aa9f8b62b2
- `RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED` — 9879c7025692390541e5bec075b633096e225aa8
- `RIMMANDRAKE_MEND_CERTIFICATE_SUMMARY_BAR_REFUSAL_CRASHED_IT` — 9879c7025692390541e5bec075b633096e225aa8
- `RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED` — eb12d7fd0b86
- `RIMMANDRAKE_KEEP_CUT_BEASTS_OFF_TEST_TIERS` — a4291f3a9d8c
- `RIMMANDRAKE_EXEMPT_QUEUE_PROJECTIONS_FROM_DEBRIS_EVERY_HELPER` — 67f6fb64cd59
- `RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES` — 129303f654
- `RIMMANDRAKE_ROUTE_MODLEDGER_OWNER_GATES_VIA_CONDUCTOR` — 294dc94beb
- `RIMMANDRAKE_BOOK_PIPE_VOID_BY_UNIT_NOT_RUN_ID` — 644a024350
- `RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE` — be042db314
- `RIMMANDRAKE_RECONCILE_FLAGSHIP_CONTRACT_WITH_DELEGATED_PICK` — d143c3e78cad
- `RIMMANDRAKE_RELEASE_CLEANSE_CLONES_RECORDS_PIN_POOL_FULL` — 53e1a63956f5
- `RIMMANDRAKE_FIX_OWED_VIEW_TEST_FILLER_NAMES_DOUBLED_WHOLE` — c06bbdb479
- `RIMMANDRAKE_DECODE_LANDING_PATCHES_AS_BYTES_STRAY_BYTE_CRASHED` — cc10cfe65d520fef2abc1dc2ef82573968adf3f1
- `RIMMANDRAKE_SEAL_SHOWCASE_EXIT_WHEN_PHASE_CRASHES_AFTER_PASSING` — 5079ad05ae
- `RIMMANDRAKE_REBUILD_DISPATCH_VIEWS_ON_EACH_LAND_RETRY` — 6eba4bcbd4
- `RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE` — 71e1181a33
- `RIMMANDRAKE_LIST_MODLEDGER_DELETIONS_ON_DAILY_DIGEST` — 8ab56652ab
- `RIMMANDRAKE_FIX_LOOK_GRANT_COUNTED_TWICE_COVERED_LOOK_FREE` — 2a780e4846ff
- `SCHEDULE_HARDEN_FAIL_CLOSED_NO_DEFAULTS` — 964d3035b6da
- `RIMMANDRAKE_HOLD_DET_CLONE_UNTIL_RETURNED` — 410d70d8ea
- `RIMMANDRAKE_SPLIT_ONLY_NAMES_LONG_LIST_CRASHES` — 48e54901198f
- `RIMMANDRAKE_SPLIT_RED_FROM_UNMEASURED_STATUS_ENTRY_LIES` — 10ee9e96c13c
- `RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS` — 2bd83d48ac
- `RIMMANDRAKE_ADMIT_TEN_WORD_FAULT_ID_INTO_KNOCKBACK_LEDGER` — 5b89d34149e9
- `RIMMANDRAKE_AMEND_SPINE_DOOR_CLAUSE_TICKET_THREE_MUST_BREAK` — 907d3e5717
- `RIMMANDRAKE_HOLD_ALL_ON_UNREADABLE_STORE_TICK_CRASHED_INSTEAD` — 1b0012a11b9f
- `RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED` — b4bf415ffd17
- `RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS` — 1b0012a11b9f
- `RIMMANDRAKE_HOLD_CODEX_DESIGNER_AT_THE_QUARTER_LEFT_LINE` — 7166566abc
- `RIMMANDRAKE_HARVEST_OWNER_WORDS_OFF_CONCEPT_ITEM_FOURTH_ASK` — 01b8370c14
- `RIMMANDRAKE_TIGHTEN_SHADOW_ACCEPT_FOUR_CLAUSES_PASS_ON_LESS` — f1a096e0ee
- `RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED` — 39631a69d4
- `SELFTEST_ASSERT_CLOSE_FIX_ACCEPTS_NAN` — 619625511c60
- `RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD` — e6bdc4d142
- `RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN` — c6581d7b06d0b3b9be104a7302bd700a46f2d87d
- `SHOWCASE_RULES_TUNE_AWAITING_STAGE_THREE` — fe17d44ecd62
- `RIMMANDRAKE_UNGATE_STEWARD_EXAM_HELPERS_WINDOW_BUDGET_AT_ZERO` — 153991c967
- `RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED` — 7a23d9bf85f4a0a137ca40791e5e44867de63807
- `RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH` — 7be8cb7053
- `RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES` — 02d5ef936e2dd2fdb3e4dd96c8af135a062e47fd
- `RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_CONDUCTOR` — 0c4cac7a1d72
- `RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL` — 0c4cac7a1d72
- `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` — 2e02223be3ee076ec88223923d80a22caaeffede
- `RIMMANDRAKE_REWRITE_BIOME_DESIGNS_UTINNI_LENS_SHIP_LEAVES_SOON` — 2a1b374678e1
- `RIMMANDRAKE_KEEP_WSLENV_IN_LIVE_PROOFS_TWENTY_SEVEN_DROP` — dd9690e05fb7
- `RUN_SELFTESTS_FIX_STDERR_EATS_MARKER` — 9ee8ed201d34
- `RIMMANDRAKE_RETURN_LOOP_WISDOM_TO_MANDRAKEWORKFLOWS_SKILLS` — 07ca0b363cf2d0a1bbd2aa98366c0f0ed0f76311
- `RIMMANDRAKE_WAIT_FOR_RIMWORLD_PAST_FIVE_SECONDS` — 83cc9cf1e66a
- `RIMMANDRAKE_BIND_CERTIFICATE_TO_WHAT_HE_SAW` — 1c46fd89fd346c51deba2ebcc630148f8b0a5dd4
- `RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT` — 1c46fd89fd346c51deba2ebcc630148f8b0a5dd4
- `RIMMANDRAKE_CLAIM_WIRED_MUST_SHOWS_THREE_MODS_BARE` — 5eca7e2809b4
- `RIMMANDRAKE_SPLIT_COVERAGE_DATED_JSON_FROM_TRAILING_SUMMARY` — 5eca7e2809b4
- `RIMMANDRAKE_STOP_FILLING_GRAFFITI_REFUSED_AT_ITS_GATE` — b19017b911
- `RIMMANDRAKE_SHORTEN_BRAKE_PASS_STEWARD_MISSED_ITS_BEAT` — 3f8e82cab78f
- `RIMMANDRAKE_NAME_SOAK_SILENT_EXIT_INTERRUPTED_LOOKS_IDLE` — 0f0871798059
- `RIMMANDRAKE_FIX_WHEA_FUTURE_ROW_HID_AS_FATAL_ZERO` — 3ef4b41e73ea
- `RIMMANDRAKE_ROUTE_SOAK_READ_VIA_TAILNET_DESKTOP_SEES_NOTHING` — e4db27874556
- `OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO` — 3ef4b41e73ea
- `RIMMANDRAKE_SCOPE_SELFTEST_LEDGER_READS_PREFLIGHT_LOG_TRIPS` — 1fe595f83e10
- `ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING` — c1651115d3
- `AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO` — c5c07b9e25
- `RIMMANDRAKE_HOLD_PENDING_BATCH_AFTER_DELIVERY_DEATH` — f29a2b7680
- `ALARM_FILING_FIX_NO_ROOM_AT_INN` — ba566f60c7
- `CHECKER_REACH_FIX_GH_DARK_SECOND` — c549cc8ab6
- `CLEANER_SANITY_REVIEW_FINISH_FULL_FILES` — 3bf4cecd5f
- `CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY` — c043da2443
- `CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES` — b47c87d04b
- `DELEGATED_DIGEST_HARDEN_MUTATION_SURVIVORS` — 68b347c069
- `DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH` — f160d57cf8
- `DRVFS_ENOMEM_FIX_ORDER_SEVEN_RUNS_DRY` — 34283c8415
- `EVIDENCE_HEAD_SEAL_REPAIR_THREE_BEHIND` — 9df1e805ad
- `LOG_BOUND_DECIDE_COLD_LOAD_ALWAYS_GUILTY` — 9d974a4e3c
- `MIRROR_PACK_REPAIR_STILL_GRUMBLING` — 1a553c5002
- `RIMMANDRAKE_HARDEN_HANDOFF_CHECK_FOUR_HOLES_CODEX_FOUND` — c04cf0314869
- `DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE` — a8e1e2e57023
- `RIMMANDRAKE_FIX_DENIED_REFUSAL_LOST_WHEN_LOG_FAILS` — a8e1e2e57023
- `RIMMANDRAKE_FIX_INCIDENT_BELLS_ONE_RING_PER_SEAT_SESSION` — a8e1e2e57023
- `RIMMANDRAKE_FIX_RUNG_AT_STAMPED_BEFORE_LOCK_WAIT` — a8e1e2e57023
- `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE` — 5860e8f8cebebdfbee959a94596daf70e8ae02bf
- `OWNER_ASKS_AUDIT_FIFTY_NINE_DEEP` — f03c025e7e
- `RIMMANDRAKE_REVISE_PILOT_BIOME_DESIGNS_WITH_FOUR_RULINGS` — b54f06306071
- `PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS` — 18178d9350
- `PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN` — e6ab733c03
- `REGRADE_SAMPLE_BUILD_NOISE_GUARDED` — df7cadb8b9
- `REPO_RENAME_SYMLINK_RETIRE_1` — e148e8c31e
- `RESTOREWAIVER_AUDIT_TEN_TAKEN_ON_TRUST` — 746fd15844
- `ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS` — 6dcfd7f682
- `SEAT_TMP_PRUNE_TESTS_LEFT_LUGGAGE` — e9221a885c
- `SLOT_HOOK_FIX_TEXT_STILL_OWNER_ONLY` — 0535dcc043
- `STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE` — 5f7d5b0d57
- `TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD` — 6607725538
- `TMP_SCRATCH_PRUNE_SIXTEEN_GIGS_NOBODY_CLAIMS` — 7385b7d55d
- `OPS_ERROR_BUDGET_DIAGNOSE_CIRG` — 22f53ea356
- `OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT` — ee749bf033
- `OPS_METRONOME_MIGRATE_CLOCKS_FENCED` — aa928335da
- `LESSONS_RETIRE_INBOX_AS_QUEUE` — 47595a6360
- `RIMMANDRAKE_REWRITE_BLUEDESERT_TO_SLIME_UTINNI_LENS` — fe304c57fe7a
- `RIMMANDRAKE_CONTINUE_LEFT_OPEN_RUNS_WITHOUT_A_HAND_RELAUNCH` — 8addfdb8bcbb
- `RIMMANDRAKE_FIX_MEAN_HELPERS_COUNTS_IDLE_GAPS_AS_RUNNING` — e4f6ecd988d9
- `RIMMANDRAKE_FIX_SLOT_SET_WORDS_KEEP_OWN_SEAT_TIME` — e4f6ecd988d9
- `RIMMANDRAKE_FIX_STREAMS_FIXTURE_LACKS_CODEX_BRAKE_KEY` — e4f6ecd988d9
- `RIMMANDRAKE_REWRITE_LANTERNDEEPS_TO_RUSTCATHEDRAL_UTINNI_LENS` — 3eeeb118bf8c
- `RIMMANDRAKE_REWRITE_THESUMP_TO_WEEPINGSTONES_UTINNI_LENS` — 80ddbabd42f9
- `RIMMANDRAKE_REWRITE_SLEEPINGICE_TO_THEROT_UTINNI_LENS` — 260f720cae97
- `RIMMANDRAKE_REQUIRE_HIS_WORDS_BEHIND_SPEAKER_OWNER_RULING_PASSED` — 085ea874b073
- `RIMMANDRAKE_MATCH_EXAMINER_TO_AUTHOR_BY_ID_NOT_LABEL` — 6ddd8a75170e
- `RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK` — 16ba7496bd694e9800538a83542434e248e932b9
- `RIMMANDRAKE_ROUTE_FLAWED_CRITERION_GAPS_OFF_DESIGNER_REWORK` — 5b8f201cfa74
- `RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH` — done by verify, no close
- `RIMMANDRAKE_MOVE_END_RECEIPT_OFF_RESULT_FILE_ROLES_FAILED` — done by verify, no close
- `RIMMANDRAKE_MEND_WRAPUP_W1_AFTER_CONTROL_END_RECEIPT` — done by verify, no close

## Filed and still open (64) — the next seat's queue

- `RIMMANDRAKE_REGISTER_EK_SELFTESTS_THIRTEEN_NO_TABLE_ENTRY_SAW` — ExplosiveKnockback test table: 13 on-disk selftests are in no test entry (walk_raid among them, which already kills both frame mutants)
- `RIMMANDRAKE_REGISTER_UNLISTED_SELFTESTS_THREE_MODS_157_UNSEEN` — Pyrelands 5, GimmeSomeSlack 13, FlowWorks 139 on-disk selftests are in no test-table entry: the certificate and blind brief never see them
- `RIMMANDRAKE_SETTLE_TRIBUTE_RIVAL_BAND_NEW_IN_CYCLE_TWO` — Graffiti: settle whose rival a tribute moves (lane-1 L1_TRIBUTE_RIVAL_BAND UNSETTLED, cycle 2)
- `RIMMANDRAKE_RECHECK_ADVANCE_CALIBRATION_TEST_PASSES_WITHOUT_ROW` — Nothing rechecks that families.maturation_advance reads CALIBRATED: selftest_maturation --submit builds its own registry (ALL PASS with the production
- `RIMMANDRAKE_READ_ODD_RESULT_SHAPE_AS_BLIND_NOT_CRASH` — worker.py kept_game_unmappable RAISES on a result.json that parses but is not a dict ([], 0) or has a non-string note ({'note': 17}) instead of keepin
- `RIMMANDRAKE_READ_UNREADABLE_PID_AS_UNKNOWN_NOT_DEAD_YET` — seat_restart: a LIVE pid whose /proc read fails reads dead: 55722bc0f9's ps fallback re-reads its birth in epoch seconds against saved clock ticks on 
- `RIMMANDRAKE_HARDEN_PIN_ANCHOR_THREE_EDGES_CODEX_FOUND` — designer_stage pin anchor (e881b97715), three edges Codex reported: an anchor that does not carry the pin is accepted if the pin appears later (the do
- `RIMMANDRAKE_HARDEN_PUBLISH_PARK_RESTORE_RACE_CODEX_FOUND` — seat_sync park (84ca416f3a): _unpark_added checks lexists then os.rename, so a save landing in between is overwritten; park dirs are named to the seco
- `RIMMANDRAKE_VERIFY_PREEXISTING_CODEX_FINDINGS_FULL_FILE_HAUL` — Pre-existing findings the FULL-FILE Codex reviews of the 2026-11-17 landings reported and this run did NOT verify (coverage_judge delta hashing and un
- `RIMMANDRAKE_RECORD_DOOR_SKIP_FOUR_LANDINGS_LEFT_NO_TRACE` — RM_PUBLISH_SKIP_PIPELINE_CHECKS only prints a line (publish.py pipeline_checks): the skip and its reason reach no commit, trailer or ledger event, so 
- `RIMMANDRAKE_UNPLACE_MACHINERY_HELPERS_FROM_MODS_SLOT_TAKEN` — maturation_now.item_mod places a Conductor helper on pipeline machinery on the mod its item notes cite by concept path, so it counts as a live run on 
- `RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS` — Extend the void rule to errored judge rounds, Designer rejections, refusal counts, the chain cap and Test Pilot verifies
- `RIMMANDRAKE_LAUNCH_UPGRADE_SECOND_WAVE_THIRTY_ONE_STILL_WAIT` — Launch the second wave of pipeline upgrade lanes when first-wave lanes free up: testq/SteveDesktop tickets, the large builds, the 12 NEEDS SPLIT, tick
- `RIMMANDRAKE_TRACE_ROLE_RUN_LOST_DONE_STRANDING_NOW_CAUGHT` — A done Designer run left the Dispatcher's tracking without role_done; find the path that drops it
- `RIMMANDRAKE_HONOUR_HOLD_BEFORE_COVERAGE_STOP_FIXER` — resolve's coverage-stop branch runs _stop_tickets before HOLDS: a held mod can get a ticket fixer launched (Codex, read not reproduced). Acceptance te
- `RIMMANDRAKE_COUNT_HAND_FIX_ON_UNBOOKED_ROAD_BACK_TICKET` — maturation_hands._fix_queue misses road-back items no fixer was booked on: a hand fixer there records no hand act (Codex, read not reproduced). Accept
- `RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO` — Slice 2 of the pipeline control surface: every other consumable as a typed account in control.py. Acceptance test in the item's ## verify, watched fai
- `RIMMANDRAKE_ADD_PIPE_QUEUE_VERBS_QUEUE_VIEW_PRINTS_MEGABYTES` — Slice 3 of the pipeline control surface: queue verbs in the control store and compact read defaults. Acceptance test in the item's ## verify, watched 
- `RIMMANDRAKE_KEY_SETTINGS_EDITS_BY_OCCURRENCE_ABAB_LOST_ONE` — maturation_hands settings_edit act ids hash only old and new values: an A->B->A->B edit sequence records the third edit under the first's id and drops
- `RIMMANDRAKE_FOLD_RECORDED_HAND_ACTS_AFTER_KNOWN_FAILS` — maturation_hands auto-folds only newly collected acts: an act recorded while _known() failed, or a record --why naming an existing item, is never fold
- `RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN` — Slice 4 of the pipeline control surface: pipe next on the shared planner, the containment drop-in, the mirror belt. Acceptance test in the item's ## v
- `RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY` — Run modcheck Suite scenes on an empty game too (the certificate's adapter covers FlowWorks only)
- `RIMMANDRAKE_SCOPE_LAND_REPLAY_TREE_AFTER_RENAME_MERGE` — land.sh replay checks the commit's paths but not the merged tree: an upstream rename of an allowed path can carry the change to an unlisted path, publ
- `RIMMANDRAKE_KEEP_AUTHOR_ON_LAND_REPLAY_COMMIT_TREE` — land.sh replay sets GIT_AUTHOR_* on git show, the left side of the pipe, so git commit-tree uses the default author and date (Codex, read not reproduc
- `RIMMANDRAKE_FIX_REAL_DIGEST_DETECTOR_BIG_NUMBER_COUNTS_GREW` — selftest_delegated_digest real-page detector reads 5-digit source counts as leaks
- `RIMMANDRAKE_SAMPLE_PYRE_NEVER_ROWS_BETWEEN_FIVE_HUNDRED_TICKS` — Pyrelands wind_burn_live: its 'never' rows (fire cap, outer lanes) are read only every 500 ticks
- `RIMMANDRAKE_GREEN_RESET_PHRASES_FOCUS_CLAIM_RED_ON_MAIN` — selftest_conductor_reset_mode (6 phrase FAILs) and selftest_focus_cap (1 FAIL) red on origin/main
- `RIMMANDRAKE_FIX_COVERAGE_JUDGE_TEN_FINDINGS_FIFTH_COUNT_CLEAN` — Ten older coverage_judge defects Codex found while reviewing the fifth count (which passed): baseline loss, unfixed bypass, slot misread, uncharged re
- `RIMMANDRAKE_FIX_ASSERTCLOSE_NAN_THREE_OTHER_SELFTESTS` — AssertClose accepts NaN in RimProperty, Visibility and JawaIonWeapons SelfTest Program.cs
- `RIMMANDRAKE_FINISH_ROLLBACK_WHEN_A_RESTORE_WRITE_FAILS` — maturation commit_move: a rollback write that fails stops the rollback, leaving the stage record moved
- `RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER` — maturation spend_rows: an earlier version's Dispatch run rows count in the next version's show/next spend
- `RIMMANDRAKE_SETTLE_PARTIAL_IMPL_TWO_INVENTORY_ROWS_UNCOUNTED` — FlowWorks and GimmeSomeSlack record.json carry impl "partial", which designer_stage refuses, so their showcase coverage cannot be counted
- `RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD` — When the old-pipeline retirement builder reports: launch every old-era ticket found still valid and unworked (the two parked of the ten included) and 
- `RIMMANDRAKE_ATTRIBUTE_MANUAL_SWITCH_BY_LOG_NOT_OLD_MARKER` — switching_plan.manual_switch takes any same-transition marker under 40 min as the plan's own (done or failed included): his repeated switch can be und
- `RIMMANDRAKE_KEEP_SHA256_REFLOG_TIPS_FORTY_CHAR_FILTER` — RIMMANDRAKE_KEEP_SHA256_REFLOG_TIPS_FORTY_CHAR_FILTER: scratch_reap safety flaw found by Codex review
- `RIMMANDRAKE_PIN_TMP_FILE_BASELINE_BEFORE_RENAME_NOT_AFTER` — RIMMANDRAKE_PIN_TMP_FILE_BASELINE_BEFORE_RENAME_NOT_AFTER: scratch_reap safety flaw found by Codex review
- `RIMMANDRAKE_COUNT_PROMISE_SCAN_FALSE_HITS_AFTER_ONE_WEEK` — promise_scan: count its false hits over the first live week, before any blocking
- `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` — Phase 2 of retiring the old pipelines: move the live parts of relentless.py and its 54 modules under names that say what they are, delete what nothing
- `RIMMANDRAKE_BRING_SECOND_WAVE_OWNER_CALLS_ON_ONE_CARD` — Bring him the second wave's owner calls on one card when he asks (SteveDesktop swap/RMA/retire, Fable re-ask, phone-alert card, handoff cull age, row 
- `RIMMANDRAKE_RETIRE_LEASE_GUARD_TWENTY_FIVE_GHOST_LEASES` — Retire the lease guard: 25 ghost leases block rimflow verbs for good
- `RIMMANDRAKE_NAME_SOAK_BLIND_MINUTES_ON_REPEATED_UNREACHABLE` — soak_read: two UNREACHABLE reads in a row say the instrument has been blind N minutes
- `RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS` — Prove the scene runner live: same verdict rows as knockback_runner.py, fewer bridge calls
- `RIMMANDRAKE_PORT_SUITES_TO_SCENE_RUNNER_PIT_EXPOSURE_FIRST` — Port more suites to jawa/run_scenes: FlowWorks pit exposure first, then EK's remaining scenes
- `RIMMANDRAKE_VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO` — Before any old biome file is deleted: a second Fable reader checks each rewrite_choices.md against its source files for ideas with no row; then he rea
- `RIMMANDRAKE_RESTAMP_PYRELANDS_CONCEPT_TREE_RED_IN_TWO_LANES` — selftest_pyrelands_round6_gaps red on main: Pyrelands concept tree cites a stale root hash (lint since 2ff90a9590)
- `RIMMANDRAKE_SEED_SCENE_LOOK_CALIBRATION_BRIM_PIT_PAIR` — Seed scene_look_judge_brief's calibration: the brim-pit pair, owner-verdicted, as planted cases with a model_check
- `RIMMANDRAKE_RESOLVE_CONCEPT_CLONE_IN_CLI_REPIN_REPO_WON` — designer_stage: CLI repin resolves the concept's clone
- `RIMMANDRAKE_REJECT_MALFORMED_DESIGNER_RESULTS_NOT_CRASH` — designer_stage: a malformed result or record is rejected, never a crash
- `RIMMANDRAKE_REFUSE_UNREADABLE_OWNER_FEED_BLIND_IS_NO_REPLY` — designer_stage: unreadable OWNER feed is UNMEASURED, not his answer
- `RIMMANDRAKE_BUILD_PACKET_BEFORE_SAVING_OPEN_RUN_PHANTOM_CHARGE` — designer_stage: build the packet before saving the open run
- `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING` — When all four biome batches have reported: gather every NEEDS HIM from the 23 designs and bring them to him grouped by theme (orbit cover and full dar
- `RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS` — North-star frame judge FAILs write no refusal-contract record
- `RIMMANDRAKE_REWRITE_SCALD_SEA_DESIGN_READ_IN_FULL` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_REWRITE_GREY_SEA_DESIGN_READ_IN_FULL` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_REWRITE_TWILIGHT_SEA_DESIGN_READ_IN_FULL` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_REWRITE_CHILL_SEA_DESIGN_READ_IN_FULL` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_RECHECK_FEVERWOOD_GREENTIDE_ABYSS_CHOICES` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_RECHECK_BLUEDESERT_TO_SLIME_CHOICES` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_RECHECK_LANTERNDEEPS_TO_RUSTCATHEDRAL_CHOICES` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_RECHECK_SLEEPINGICE_TO_THEROT_CHOICES` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_RECHECK_THESUMP_TO_WEEPINGSTONES_CHOICES` — Biome rewrite follow-up, Fable: read every source in full, add the missing rows, repair the design, mark each biome DELETE-READY yes or no (or, for a 
- `RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED` — Retire the Setter and arbiter seams in role_launch: both act only on 102 Relentless-era exams and every launch is refused (family relentless OFF). Acc
- `RIMMANDRAKE_ENACT_SEARCH_NEVER_PAUSES_SEA_FLOOR_VERY_CONCEALED` — Enact his 2026-11-18 ruling in every place that says otherwise: no place pauses the Empire's orbital search indefinitely (this changes the 2026-08-05 
- `RIMMANDRAKE_LAUNCH_TWO_RUNS_REFUSED_BY_FULL_POOL` — When a pool clone frees: launch the Sleeping Ice to Rot second reader (item RIMMANDRAKE_RECHECK_SLEEPINGICE_TO_THEROT_CHOICES, brief reader_sleepingic

## Commits

```
6ad58a7d08 ledger: owner ruling that no place pauses the search and a sea floor is top-tier cover; enact ticket; waiting launches filed as a debt
11a050e9d8 designer_stage: CLI repin resolves the concept's clone (RIMMANDRAKE_RESOLVE_CONCEPT_CLONE_IN_CLI_REPIN_REPO_WON)
a164008a3e era split move 3: Setter seam to rimflow/item_exam.py, arbiter seam to stage_dispute.py, checker box to checker_box.py
568f70177b ledger: RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE clone bundled
5b8f201cfa designer_stage: a flawed-criterion or advisory gap is not Designer rework (RIMMANDRAKE_ROUTE_FLAWED_CRITERION_GAPS_OFF_DESIGNER_REWORK)
526720aef0 ledger: RIMMANDRAKE_REWRITE_GREY_SEA_DESIGN_READ_IN_FULL note
ce8439a20a conversations: catch-up 1 record(s)
a89d87b8b2 ledger: detached run on RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE ended
56555e78f8 ledger: slot allocator finding 1 decided (b), delegated under Evidence-for-Ask
16ba7496bd judge: Codex repair check of the fold (top-level final answer only, look history kept across skipped runs, pass-2 staging errors are could-not-run, no Pillow refuses)
ccb3965dea ledger: owner on measured dark versus hidden and a unique reason to visit every biome; two second readers wait for a pool slot
cd1de1c681 ledger: old-era sweep notes, guard-owed, keep and owner rows
6ddd8a7517 designer_stage: examiner vs author compared by agent id (RIMMANDRAKE_MATCH_EXAMINER_TO_AUTHOR_BY_ID_NOT_LABEL)
11974f604c ledger: nine biome follow-up tickets (four seas read in full, five second-reader checks); two Conductor debts on the biome rewrite
18ccc458e0 judge: fold the north-star frame judge into the scene-look brief (judge_cli.py runs pass 1, bar-blind, before its unchanged pass 2)
86c92d6361 ledger: OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO clone bundled
085ea874b0 designer_stage: speaker owner needs an OWNER event holding his words (RIMMANDRAKE_REQUIRE_HIS_WORDS_BEHIND_SPEAKER_OWNER_RULING_PASSED)
00447c3e1b conversations: catch-up 1 record(s)
dc7647743a ledger: detached run on OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO ended
4351d8034c agents: three false lines in the digest that is these agents' only source of rules
... 526 more: git log --oneline 1b8be9ae3e..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-17T19:16:24Z

Working tree clean apart from untracked `Transient/`.

