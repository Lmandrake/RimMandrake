# BENCH_REBOOT_HANDOFF_202611200206 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611192213`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner spent this sitting on WHY reviews stopped converging, and he ruled a new review method by card at 5:54 PM PST 2026-11-19. Read `D:\Luke\dev\MandrakeWorkflows\codefix-strategies\README.md` before you touch any review, clean/dirty or pipeline-repair question. Three things are easy to get wrong: (1) the old loop was NOT one pass (a fixed file stayed dirty until a fresh blind reader passed it); (2) the clean/dirty policy did not cause the ticket churn, repeated Codex rounds on fast-changing pipeline code did; (3) start no new pipeline repair wave unless a row blocks a mod's next step or a real run failed (his concern, my stated practice, not yet a written ruling). FlowWorks and GimmeSomeSlack are switched ON and are the live probe of the pipeline; Pyrelands is held by the Conductor.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Waiting for him, none urgent:** the churn card (`RIMMANDRAKE_READ_SPEC_SCAN_RESULT_THEN_CARD_HIS_OPTIONS`); the biome questions, now five plus Contagion screen and Scald steam clock, and the recount of 29 silently passed ship ideas (`RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING`); the Lodestar icon A, B or C; his 12 owner tickets and the Gelatinous Slime giant look; whether a mod's locked bars count as its page (`RIMMANDRAKE_CARD_MOD_BARS_AS_PAGE_SHIP_CHECK_GREY`); FlowWorks bars to 0.2.0 (`RIMMANDRAKE_CARD_FLOWWORKS_FOUR_BARS_TO_NEXT_VERSION`).
- **Decided for him today, each undoable:** FlowWorks switched on 4:10 PM PST and GimmeSomeSlack 4:20 PM PST (`./pipe off <Mod>`); 94 owner-bound tickets re-labelled as not needing him; three rule groups moved out of CLAUDE.md (pointers stay); rm-testpilot.md accepted at STE 3.33; the mod-ledger cutover deferred to 2026-11-22; Pyrelands held until its tree is restamped and re-signed.
- **The MandrakeWorkflows study is in a PUBLIC repo** (commit 64a9fb35e1, update in progress at wrap). The manifest that decides what goes public is not on this machine, so whether the folder is published is UNMEASURED.
- **I gave him three wrong clock times and two wrong claims today** (policy caused churn; old re-review optional). Each was corrected to him and on the ledger; the study records them.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. The Conductor's pointers each cite an open owed id too: file the act first (`rimflow file <ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; --check runs `owed.py check-pointers`. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` — deferred by the Conductor: it rewires 76 writes of the live stage record and clears no blocking row; waits until 2026-11-22; NEXT: recheck after one mod has run a step; launch it only then (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_CONTROL_STORE_COUNTS_AND_TICK_PAUSES` — 8 of 12 closed; 4 left open with LEFT OPEN notes that I did not read; NEXT: read the four notes with `rimflow show` and decide each; launch nothing that blocks no mod step (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_MODLEDGER_CUTOVER_AND_SEAL_EMPTY_SHARD` — 4 of 5 closed; the fifth is the deferred cutover; parked to 2026-11-22; NEXT: leave parked; drop stage.json from store_write_census.py's store list when the cutover item is next worked (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_RED_SELFTESTS_ONE_SWEEP_NO_NEW_ONES` — its run was killed (exit 143) at 3:44 PM PST with no result, cause UNMEASURED (machine load average was about 40); not relaunched; NEXT: relaunch it only if a red selftest blocks a publish or a mod step; brief is briefs_20261119/lanes_launch/<item>.md (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_STATUS_PAGES_READING_DEAD_LOGS` — 5 of 8 done; the VV matrix clock fix af7ebfd11990 is unproven by a full run; two tickets wait on a Conductor call (prune priority list, health verdict reader); NEXT: rerun the VV matrix clock once and close INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING with --live, or note why not (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_STEVE_LANE_WORKER_AND_GAME_STOPS` — 7 of 13 closed; 6 wait for the SteveDesktop soak to end; parked to 2026-11-22; NEXT: check the soak's own start time first (helper says it ends 2026-11-21 03:29Z = Fri 7:29 PM PST, owed item says 5:30 PM PST), then read the soak (RIMMANDRAKE_READ_STEVE_SOAK_AT_24H_72H_REBOOT_PROVEN)
- `RIMMANDRAKE_HARDEN_BRIDGE_COMPANION_TOOLS_WITHOUT_THE_GAME` — 3 of 6 closed; the new companion DLL is deployed (game copy matches build) but loads only at the next game start; live proof UNRUN; NEXT: at the next game start run `python.exe src\RimMandrake\bridgetools\prove_true_tool_outcomes.py` before trusting GimmeSomeSlack visit 2 results (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE_FOUR_TESTS_FIRST` — live since about 4:29 PM PST; FlowWorks was switched on by the Conductor at 4:10 PM PST; NEXT: read its result when it wakes you, then do RIMMANDRAKE_SEND_FLOWWORKS_GAPS_TO_DESIGNER_AFTER_CYCLE_FOUR and RIMMANDRAKE_CARD_FLOWWORKS_FOUR_BARS_TO_NEXT_VERSION
- `RIMMANDRAKE_RESTAMP_PYRELANDS_CONCEPT_TREE_RED_IN_TWO_LANES` — not restamped: `concept_tree write` would also void the coverage judge's 2026-11-17 signature because the north star changed after signing; parked to 2026-11-21; Pyrelands stays OFF; NEXT: read what changed in the Pyrelands north star since 2026-11-17, then choose: restamp and re-sign, or a Designer pass over the 24 leaves first (I lean to the second); tracked under RIMMANDRAKE_SWITCH_ON_PYRELANDS_AND_SLACK_WHEN_ROWS_CLEAR
- `RIMMANDRAKE_REWRITE_CHARTER_AND_AGENT_POLICY_EVERY_SEAT_READS` — rewrite is live (5d7e6397e2, b9463820e3); the Conductor accepts check 2's four reported losses; `rimflow close` was refused for want of a recorded pass; NEXT: run `rimflow verify` on b9463820e3 with the result file as evidence, then close with --sha b9463820e3 (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING` — run 1 and five batches landed; orders 6 to 17 of the batch plan are not started; NEXT: do RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT a few at a time, and RIMMANDRAKE_COLLECT_REWRITE_CONFLICTS_UNDEFINED_TERMS_ONE_LIST from the result files in design/specs/2026-11-19-plain-english-rule-docs/results/
- `RIMMANDRAKE_REWRITE_SUBAGENT_FILES_SHARED_BLOCK_SIX_COPIES` — landed (47d1dad056, 630ca91c90); the Conductor accepted rm-testpilot.md at STE 3.33 by note; item still open; NEXT: record the pass with `rimflow verify` and close it (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_STOP_SHARED_COPIES_OUTLIVING_THEIR_LENDER` — not looked at in this sitting; state unknown to me; NEXT: run `rimflow show RIMMANDRAKE_STOP_SHARED_COPIES_OUTLIVING_THEIR_LENDER` and act on its last note (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)

- `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG` — detached Opus run launched 6:05 PM PST, enacts his card on the review method (rule text and the FLAGGED state); NEXT: read its result at its wake, tell him, then launch RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET with the card text pasted in its brief (`card_capture.py show`), brief folder briefs_20261119/review_method/ (owed: `RIMMANDRAKE_READ_REVIEW_METHOD_RUNS_THEN_LAUNCH_SCAN`)
- `RIMMANDRAKE_REVIVE_CLEAN_DIRTY_TREEMAP_ON_STANDING_TABS` — detached Opus run launched 6:05 PM PST; NEXT: read its result at its wake and give him the page's full Windows path (owed: `RIMMANDRAKE_READ_REVIEW_METHOD_RUNS_THEN_LAUNCH_SCAN`)
- `RIMMANDRAKE_DOCUMENT_REVIEW_LOOPS_IN_CODEFIX_STRATEGIES` — study pushed to MandrakeWorkflows (64a9fb35e1); the update for his 5:54 PM card was in progress or just landed at wrap; NEXT: confirm the update commit is pushed (`git -C ~/dev/MandrakeWorkflows log -2 --oneline`), update it again when the method and scan runs land, then close
- `RIMMANDRAKE_SWITCH_ON_PYRELANDS_AND_SLACK_WHEN_ROWS_CLEAR` — GimmeSomeSlack is ON (4:20 PM PST) and waits its turn behind FlowWorks; Pyrelands OFF; NEXT: restore the missing bar cords_join_stubs_on_position_and_slope in GimmeSomeSlack locked_bars.json before any exit decision (RIMMANDRAKE_CHECK_THREE_COVERAGE_HOLES_CLOSED_WITH_TEST_RED), and launch helpers with `--env RM_CONTROL_MOD=none` so they hold no mod slot
- `RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY` — miner fixed and three pilots re-mined; the last step is a fresh judge that did not mine; NEXT: launch an rm-judge on fresh samples only after the mods' own work is served (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_REPORT_DAILY_FILED_COUNT_AFTER_FILING_GATE_STARTS` — owed to him; NEXT: on 2026-11-23 count tickets filed and ended per day for 2026-11-20 to 2026-11-23 from the ledger shards and report
- `RIMMANDRAKE_LAUNCH_ELEVEN_RARE_FAILURE_LANES_BRIEFS_ARE_READY` — 10 of 11 lanes launched and reported; the retired-era rename lane is NOT launched, and he asked to weigh pipeline work first; NEXT: leave the rename lane unlaunched until a mod has run a step, then decide

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A helper's keyword count contradicted the rule text and I repeated it to the owner; read the rule text first (filed: infrastructure/state/lessons/20261120T020658Z-BENCH-before-repeating-helper-s-finding-about.md)
- A calibration status read edited judge_calibration.json and blocked ./sync (filed: infrastructure/state/lessons/20261115T132719Z-BENCH-calibrate-no-run-writes-registry.md)
- A time written into a note must come from `date` in the same command (filed: infrastructure/state/lessons/20261120T001210Z-BENCH-time-written-into-ledger-note-or.md)
- 16 detached runs at once put the machine's load average near 40 and a timing test flaked; one lane was killed with no result (see: infrastructure/state/items/RIMMANDRAKE_FIX_RED_SELFTESTS_ONE_SWEEP_NO_NEW_ONES note of 2026-11-19)
- A repair helper whose ticket title names a mod holds that mod's one live slot; launch with `--env RM_CONTROL_MOD=none` (see: /mnt/d/ClaudeWork/rimmandrake/conductor/readiness_refresh_20261119.md section 4)

## Closed since the last handoff (68)

- `RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE` — c776601fe268
- `RIMMANDRAKE_READ_MATURATION_POINTS_RESULT_AT_ITS_WAKE` — 13f1587bd7
- `RIMMANDRAKE_MAKE_COMPANION_DEPLOY_ATOMIC_HELD` — 98e81846fcc6
- `RIMMANDRAKE_FIX_ROLE_UNIT_STAMP_SELFTEST_RED_ON_MAIN` — 328611932dea
- `RIMMANDRAKE_LAUNCH_MINER_FIX_AND_TIMING_LIMIT_BOTH_WAIT` — 8d41d27910
- `RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT` — 381db58f594a
- `RIMMANDRAKE_KEEP_STEVE_PLAYER_LOG_PER_ATTEMPT_SEVENTEEN_BLIND` — 980b2efc6f1d
- `RIMMANDRAKE_FIX_WORKER_REUSES_BAD_GAME_COSTS_TWO_JOBS` — 29beb482a4
- `RIMMANDRAKE_HIDE_SPEND_IN_PROMPTS_COST_LINE_SURVIVED` — f5510dac9c76
- `RIMMANDRAKE_TYPE_PILOT_STREAK_AS_ITEM_ACCOUNT_ALREADY_ORDERED` — 0197f111d3bb
- `RIMMANDRAKE_READ_FOREIGN_DEF_NOT_FOUND_AS_LIST_FACT` — 1c39a9edc4b6
- `RIMMANDRAKE_QUIET_CURED_RED_SERIES_GONE_MEANS_GREEN` — 2bc54529df4f
- `RIMMANDRAKE_REBUILD_REQUIRED_CHECKS_MANIFEST_SIX_MODS_STALE` — 1c39a9edc4b6
- `RIMMANDRAKE_REFUSE_GSS_GATE_UNDER_PYTHON_EXE_ALWAYS_RED` — 1c39a9edc4b6
- `RIMMANDRAKE_RERUN_TEST_TABLE_BEFORE_MOD_LANDING_CENSUS_SKIPPED` — 85f388636e4b
- `RIMMANDRAKE_TAKE_EIGHTY_ONE_OBVIOUS_OWNER_TICKETS_REPORT_UNREAD` — 8d41d27910
- `RIMMANDRAKE_CLOSE_DETACHED_ITEM_AT_RUN_END` — ec49db3c3a
- `RIMMANDRAKE_FIX_VALIDATION_CORE_FOREIGN_DEFS_AND_GATES` — 85f388636e4b
- `RIMMANDRAKE_REPAIR_CONTINUE_STEP_FLAWS_CODEX_FOUND_SEVEN` — ec49db3c3a
- `RIMMANDRAKE_ADMIT_PAUSED_FLYER_READS_AT_BRIDGE_TAKE` — eba1e8b81341
- `RIMMANDRAKE_ANNOTATE_FOLD_MEMORY_BESIDE_STANDING_WORK_COVER` — e36cec36427c57eb17d433cc02f1c512af3075f1
- `RIMMANDRAKE_REFUSE_MALFORMED_IDS_CLOSE_RUN_CRASHES_INSTEAD` — e36cec36427c57eb17d433cc02f1c512af3075f1
- `RIMMANDRAKE_REVALIDATE_INPUTS_BEFORE_REFUSAL_STALE_THIRD_STRIKE` — e36cec36427c57eb17d433cc02f1c512af3075f1
- `RIMMANDRAKE_KEEP_STAGE_JSON_DESIGNERS_LEDGER_READS_HOMONYM_NAMED` — a0409779a591
- `RIMMANDRAKE_SPARE_EXPERIENCE_GAPS_FROM_BAR_WORD_DETECTOR` — e36cec36427c57eb17d433cc02f1c512af3075f1
- `RIMMANDRAKE_UNBLOCK_CONCEPTS_WHOSE_BLOCKER_CLOSED_DAYS_AGO` — 69ca12d82197a526b6a0710bd88aeffd6ac6797e
- `RIMMANDRAKE_STOP_STEVE_GAME_FORCE_KILL_LEFT_IT_RUNNING` — d712479dfb70
- `RIMMANDRAKE_SEAL_JUDGE_SHARD_FROM_SYNCED_CLONE_SEALED_EMPTY` — 1df7a8912052
- `RIMMANDRAKE_SETTLE_PARTIAL_IMPL_TWO_INVENTORY_ROWS_UNCOUNTED` — 69ca12d82197a526b6a0710bd88aeffd6ac6797e
- `RIMMANDRAKE_TRACE_PHONE_IMAGE_TMP_FILE_VANISHED_ONCE` — 1df7a8912052
- `RIMMANDRAKE_MIRROR_KNOCKBACK_STAGE_LEDGER_SAYS_OFFLINE_BUILD` — 1df7a8912052
- `RIMMANDRAKE_FIX_JUDGE_GATES_AND_DESIGNER_CLOSE_CRASHES` — e36cec36427c57eb17d433cc02f1c512af3075f1
- `RIMMASTER_FIX_AGENT_GAME_EVENTS_FILED_AS_OWNER` — eba1e8b813
- `RIMMANDRAKE_BOUND_BRIDGE_MAIN_THREAD_WORK` — 3c8b49c43666
- `RIMMANDRAKE_WAIT_LOAD_READY_UNTIL_CURRENTMAP_SET` — 3c8b49c43666
- `RIMMANDRAKE_APPLY_83_BIOME_ANSWERS_FOUR_CHANGE_A_DEFAULT` — 7894424d640fc31e5602351916ed310f4a8b8444
- `RIMMANDRAKE_RETIRE_ARCHMAGI_LIVE_ROWS_DEAD_SINCE_NOV_SIX` — 8edeb01ba1fd
- `RIMMANDRAKE_NAME_SOAK_BLIND_MINUTES_ON_REPEATED_UNREACHABLE` — 3aaf6b39d835
- `RIMMANDRAKE_WIRE_STREAMS_GAME_STATE_OFF_A_FROZEN_SNAPSHOT` — b4a763fabb78
- `RIMMANDRAKE_SKIP_WRAPUP_ROWS_A_LIVE_UNIT_CARRIES` — 195a94ec96
- `RIMMANDRAKE_SPEED_BRAKE_RELEASE_PASS_MISSES_ITS_BEAT` — a3460537afab
- `RIMMANDRAKE_GUARD_HAND_LAUNCH_AGAINST_DISPATCHER_TWIN_RUN` — 174ce562bae4
- `RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS` — 994f9807c1a1
- `RIMMANDRAKE_RESERVE_PUBLISH_BEAT_STARVED_THIRD_STUCK_ALARM` — 994f9807c1a1
- `RIMMANDRAKE_STRIP_SPEND_TALK_FROM_CARD_BRIEFS_HAND_CUT` — 9850da2ca2
- `RIMMANDRAKE_UNJAM_DISPATCH_CLONE_UNTRACKED_TWIN_FROZE_IT` — 994f9807c1
- `RIMMANDRAKE_CHARGE_SHARED_OUTAGE_ONCE_FORTY_FIVE_DEATHS` — 0197f111d3bb
- `RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE` — 9850da2ca2
- `RIMMANDRAKE_RETRY_PUBLISH_ON_INDEX_LOCK_FAILED_TWICE_RUNNING` — 9850da2ca2
- `RIMMANDRAKE_SET_HELPER_CLONE_NOREPLY_GMAIL_SLIPS_ONTO_PUBLIC` — 9850da2ca2
- `RIMMANDRAKE_CLOSE_DETACHED_RUN_ENDS_AND_CLONE_LEFTOVERS` — 9850da2ca2
- `RIMMANDRAKE_DEFEND_OR_DROP_ONE_SECOND_LIMIT_FLAKED_PUBLISH` — aa14c13a2b77
- `RIMMASTER_FIX_REMOTE_TAKE_HOLDS_LOCK_NOBODY_READS` — 98ba034b57fb
- `RIMMANDRAKE_STOP_GAME_B_TRIAL_LEFT_RUNNING_BLOCKS_STEAM` — b541e5dc39
- `RIMMANDRAKE_REWRITE_OPERATIONS_ROLE_ONE_OF_TWO_SWITCHED_ON` — 6b68cee0f8d0
- `RIMMANDRAKE_REWRITE_RESCUE_AND_WALK_ROLES_PIPELINE_NAMES_THEM` — b1ea74e5446b
- `RIMMANDRAKE_STAMP_STAGE_SPEND_ROWS_ONE_UNIT` — 09fffd6665b5
- `RIMMANDRAKE_RELABEL_SPEND_PRINTERS_STILL_V1` — 09fffd6665b5
- `RIMMANDRAKE_ALLOW_REWRITE_BATCH_ITS_ONE_MEANING_READER` — 47d1dad056ac2bcb8717affca52c7e73fbb304c7
- `RIMMANDRAKE_REFRESH_READINESS_LISTS_ONLY_BLOCKER_FIXED_AT_TWO` — 20f238d1f5
- `RIMMANDRAKE_FIX_REDUCER_SKIPS_LINES_ABOVE_LATE_VERSION_OPEN` — 96474969d710
- `RIMMANDRAKE_MOVE_BIOME_FEATURE_JUDGE_RULES_OUT_POINTERS_STAY` — 3bd830b0ec9cb9e050144f74b460fd570cf1f9fc
- `RIMMANDRAKE_REWRITE_CONDUCTOR_FILES_LONGEST_ROLE_FILE` — 02e4b2a92372be1c260078f10a4d6ed05070b55e
- `RIMMANDRAKE_ENACT_CLEAN_MEANS_PROMISES_TESTED_ONE_FIX_ROUND` — 55fb725cec62
- `RIMMANDRAKE_FLAG_NUMBER_ONLY_DIFFS_IN_MATURATION_NEXT` — 2c71850741ff
- `RIMMANDRAKE_LIST_THINNEST_MARGINS_IN_CERTIFICATE_RUN` — 2c71850741ff
- `RIMMANDRAKE_FIX_MATURATION_BRIEFS_AND_SPEND_ROWS` — 2c71850741ff
- `RIMMANDRAKE_AMEND_REVIEW_RULE_MINOR_FINDINGS_STAY_ON_POLISH` — 62f3aef1f01fbd3887bea7aff867a394cce9adde

## Filed and still open (30) — the next seat's queue

- `RIMMANDRAKE_DEFINE_STAMP_ONLY_RELAY_LINE_COLD_READER_STUCK` — Find what 'Game-state relays are stamp-only' means (standing_rulings.md §The bridge is passed through one file, ./game code) and rewrite that CLAUDE.m
- `RIMMANDRAKE_HARDEN_BRIDGE_COMPANION_TOOLS_WITHOUT_THE_GAME` — 3 of 6 closed; the new companion DLL is deployed (game copy matches build) but loads only at the next game start; live proof UNRUN; NEXT: at the next game start run `python.exe src\RimMandrake\bridgetools\prove_true_tool_outcomes.py` before trusting GimmeSomeSlack visit 2 results (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_CONTROL_STORE_COUNTS_AND_TICK_PAUSES` — 8 of 12 closed; 4 left open with LEFT OPEN notes that I did not read; NEXT: read the four notes with `rimflow show` and decide each; launch nothing that blocks no mod step (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_MODLEDGER_CUTOVER_AND_SEAL_EMPTY_SHARD` — 4 of 5 closed; the fifth is the deferred cutover; parked to 2026-11-22; NEXT: leave parked; drop stage.json from store_write_census.py's store list when the cutover item is next worked (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_STEVE_LANE_WORKER_AND_GAME_STOPS` — 7 of 13 closed; 6 wait for the SteveDesktop soak to end; parked to 2026-11-22; NEXT: check the soak's own start time first (helper says it ends 2026-11-21 03:29Z = Fri 7:29 PM PST, owed item says 5:30 PM PST), then read the soak (RIMMANDRAKE_READ_STEVE_SOAK_AT_24H_72H_REBOOT_PROVEN)
- `RIMMANDRAKE_FIX_RED_SELFTESTS_ONE_SWEEP_NO_NEW_ONES` — its run was killed (exit 143) at 3:44 PM PST with no result, cause UNMEASURED (machine load average was about 40); not relaunched; NEXT: relaunch it only if a red selftest blocks a publish or a mod step; brief is briefs_20261119/lanes_launch/<item>.md (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_FIX_STATUS_PAGES_READING_DEAD_LOGS` — 5 of 8 done; the VV matrix clock fix af7ebfd11990 is unproven by a full run; two tickets wait on a Conductor call (prune priority list, health verdict reader); NEXT: rerun the VV matrix clock once and close INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING with --live, or note why not (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_REWRITE_RULE_DOCS_PLAIN_ENGLISH_LOSE_NOTHING` — run 1 and five batches landed; orders 6 to 17 of the batch plan are not started; NEXT: do RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT a few at a time, and RIMMANDRAKE_COLLECT_REWRITE_CONFLICTS_UNDEFINED_TERMS_ONE_LIST from the result files in design/specs/2026-11-19-plain-english-rule-docs/results/
- `RIMMANDRAKE_SKIP_ZOMBIES_IN_MARKER_SCAN_ONE_DEFUNCT_BLINDS` — role_launch.scan_marked calls the whole scan blind when one zombie of this uid is newer than the run: a zombie's environ cannot be read, and the scan 
- `RIMMANDRAKE_CHECK_THREE_COVERAGE_HOLES_CLOSED_WITH_TEST_RED` — RIMMANDRAKE_SETTLE_PARTIAL_IMPL_TWO_INVENTORY_ROWS_UNCOUNTED was closed while its acceptance test still fails (showcases exit 1). Check that the three
- `RIMMANDRAKE_MEASURE_CLONE_LAG_FROM_LAST_PULL_CHURN_TRIPS` — maturation.clone_behind_min counts from the last exactly-level tick, so steady origin churn trips it while the dispatch clone fast-forwards every 90 s
- `RIMMANDRAKE_REWRITE_SUBAGENT_FILES_SHARED_BLOCK_SIX_COPIES` — landed (47d1dad056, 630ca91c90); the Conductor accepted rm-testpilot.md at STE 3.33 by note; item still open; NEXT: record the pass with `rimflow verify` and close it (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_REWRITE_CHARTER_AND_AGENT_POLICY_EVERY_SEAT_READS` — rewrite is live (5d7e6397e2, b9463820e3); the Conductor accepts check 2's four reported losses; `rimflow close` was refused for want of a recorded pass; NEXT: run `rimflow verify` on b9463820e3 with the result file as evidence, then close with --sha b9463820e3 (owed: `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`)
- `RIMMANDRAKE_REPORT_CLEAN_SHARE_HISTORY_TREEMAP_WAS_ALL_GREEN` — When the clean-share census reports (clean_share_history_20261119.md): tell him why the old clean job converged, and whether the treemap can be pointe
- `RIMMANDRAKE_FIX_KEEP_CHECK_MISPAIRS_BACKTICKS_ON_CHARTER` — rule_doc_lint.py keep pairs backticks across paragraphs, so on the old CHARTER.md it reads code as prose and misses a lost code span
- `RIMMANDRAKE_COLLECT_REWRITE_CONFLICTS_UNDEFINED_TERMS_ONE_LIST` — Collect the conflicts between files and the 'could not determine' lines from every plain-English rewrite batch into one list; settle the Conductor's; 
- `RIMMANDRAKE_TRACE_REMINE_NEAR_TWIN_WRITTEN_WITHOUT_ITS_REASON` — A --read re-mine of GimmeSomeSlack (2026-11-19 23:47Z) appended finding:RIMMANDRAKE_REWORD_GSS_NO_PIPE_BAR_POLES_ON_PURPOSE (BACKFILL:94e3b1f8ce1e3c07
- `RIMMANDRAKE_SWITCH_HEALTH_BOARDS_TO_PAGE_CLEAN_RECORD_LINGERS` — Health boards still count CLEAN from the review record; switch them to the page meaning of check
- `RIMMANDRAKE_SWITCH_ON_PYRELANDS_AND_SLACK_WHEN_ROWS_CLEAR` — Switch Pyrelands on when the concept tree restamp lands; for GimmeSomeSlack deploy the bridge companion (build.py --gm --apply, game down) after the c
- `RIMMANDRAKE_PIN_DISPATCH_SELFTEST_BRIDGE_READ_FLAKED_ONE_PUBLISH` — selftest_maturation_dispatch reads the live bridge in its cert gate checks: a held bridge failed one publish
- `RIMMANDRAKE_CARD_MOD_BARS_AS_PAGE_SHIP_CHECK_GREY` — Card him: under the promise rule a mod's ship check reads NO PAGE (Graffiti 38 files). Options: the mod's locked bar list and test table count as its 
- `RIMMANDRAKE_REPORT_DAILY_FILED_COUNT_AFTER_FILING_GATE_STARTS` — Report to him the tickets filed and ended per day for 2026-11-20 to 2026-11-23, to show whether the filing gate and the new clean rule cut the inflow
- `RIMMANDRAKE_DOCUMENT_REVIEW_LOOPS_IN_CODEFIX_STRATEGIES` — When the origin and three-gaps reports land: write the whole review-convergence study (history, diagnosis, data, the rule now) into MandrakeWorkflows 
- `RIMMANDRAKE_RECALIBRATE_CODE_REVIEW_BRIEF_ONE_PARAGRAPH_UNSET_IT` — Recalibrate the code_review brief: the polish amendment of 2026-11-19 changed roles/code_review.md, so its brief hash no longer matches and the family
- `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG` — Enact his card of 2026-11-19 5:54 PM PST on the review method: the reviewer fixes a significant finding on the spot with a test seen failing then pass
- `RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET` — Build the standing scan his card of 2026-11-19 orders: when idle, a Sonnet 5.5 helper reads code files unchanged for 7 days or more, mod content first
- `RIMMANDRAKE_REVIVE_CLEAN_DIRTY_TREEMAP_ON_STANDING_TABS` — Revive the clean/dirty treemap (codebase_health.py) and put it in the standard set of desktop visualizations, as his card of 2026-11-19 orders; propos
- `RIMMANDRAKE_CARD_FLOWWORKS_FOUR_BARS_TO_NEXT_VERSION` — Card him after FlowWorks blind cycle 4 reports: move the two bars added after the lock (inv_geyser_tub, inv_liquid_coating) to 0.2.0, and either add n
- `RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT` — Launch the remaining batches of design/specs/2026-11-19-plain-english-rule-docs/batch_plan.md (orders 6 to 17; standing_rulings.md is one batch in ses
- `RIMMANDRAKE_SEND_FLOWWORKS_GAPS_TO_DESIGNER_AFTER_CYCLE_FOUR` — After FlowWorks blind cycle 4 reports: read its result; send the mod's own gaps (missing north-star lines, the post-lock bars per his card answer) to 

## Commits

```
aa908c5abf ledger: RUNNER ingest of 0 testq job(s)
b57a0b2520 ledger: his card on the review method, three items filed
d51e27a865 ledger: RUNNER ingest of 0 testq job(s)
6085684881 ledger: RUNNER ingest of 0 testq job(s)
6ba867baf5 ledger: DISPATCHER notes (1)
e37595d5b5 ledger: RUNNER ingest of 0 testq job(s)
34119dad2d ledger: RUNNER ingest of 0 testq job(s)
1e7fdafaa7 ledger: RUNNER ingest of 0 testq job(s)
bab7903dd0 ledger: RUNNER ingest of 0 testq job(s)
ff008b5761 ledger: RUNNER ingest of 0 testq job(s)
a578108fcb ledger: RUNNER ingest of 0 testq job(s)
2bfbea4c75 ledger: RUNNER ingest of 0 testq job(s)
80dd36bb3a ledger: RUNNER ingest of 0 testq job(s)
643757acda ledger: RUNNER ingest of 0 testq job(s)
bcbb9ee7a0 ledger: RUNNER ingest of 0 testq job(s)
110749932b ledger: RUNNER ingest of 0 testq job(s)
11667f17d5 ledger: RUNNER ingest of 0 testq job(s)
36add5df7e ledger: RUNNER ingest of 0 testq job(s)
614b6903d2 ledger: DISPATCHER notes (1)
1676f11b0a seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose, settled concept folders)
... 293 more: git log --oneline 13f1587bd7..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-20T00:16:43Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
 M infrastructure/state/ledger/events/BENCH.jsonl   (this Conductor window: ledger events and item prose of this sitting, published with this handoff)
?? infrastructure/state/items/RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET.md   (this Conductor window: ledger events and item prose of this sitting, published with this handoff)
?? infrastructure/state/items/RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG.md   (this Conductor window: ledger events and item prose of this sitting, published with this handoff)
?? infrastructure/state/items/RIMMANDRAKE_REVIVE_CLEAN_DIRTY_TREEMAP_ON_STANDING_TABS.md   (this Conductor window: ledger events and item prose of this sitting, published with this handoff)
```

