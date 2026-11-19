# BENCH_REBOOT_HANDOFF_202611190625 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611190010`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
He stopped the Codex review cycle on pipeline code at 8:22 PM PST 2026-11-18 ("Go ahead and stop the review growth cycle now. I don't want to pay for that anymore."): **no brief may order a Codex or GPT code review of pipeline code, and no ticket is filed from a review finding, until he turns it back on.** Every relaunch brief appends `/mnt/d/ClaudeWork/rimmandrake/conductor/briefs_20261118/_addendum_no_review.md`. Why, measured: `design/specs/2026-11-18-review-growth-cycle/00-problem.md` (the control store drew 15, 11, 15 claims per round, 78 to 100 percent polish, most about the previous round's fix; nothing states where a component stops). The fix is being DESIGNED with him (`RIMMANDRAKE_DESIGN_REVIEW_TREADMILL_FIX_COUNT_WAS_FLAT`, a Fable draft running); enact nothing from the draft without his word. Second thing, same night: a stop order on one thing is not a hold on the rest. This window sat idle 8:46 to 10:15 PM PST "holding for him" and he said "Don't hold for me." / "You were stuck doing nothing. That sucks!" Before carding any question, grep his answers (`owner_rulings.py --grep`): the gate-order question was asked twice.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **The treadmill design draft** (`design/specs/2026-11-18-review-growth-cycle/01-design.md`, when the Fable run lands it): read it yourself first, then bring him the options and its two or three decisions on one question card. This is the one thing he was told he is needed for.
- **Biome questions by theme, one sitting** (owed `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING`): all 23 land biomes now have a second read; each recheck item's final note lists its NEEDS HIM lines by theme (roughly 80 in all, a guess, not totalled). Deletion of old biome files waits on his word after he reads the choices pages; Forge, Rot and Stillsand are NOT delete-ready until `RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING` reports.
- **Delegated calls he can veto:** gate order ruled final (exam first; only touched scenarios re-run; built, 84ef53b231); the cutover check measures writers at run time; helpers are placed on a mod only by their launch record; the dispatch-cut ticket dropped; his polish filter applied to the findings fixer (problems only, polish to `D:\ClaudeWork\rimmandrake\conductor\pipeline_polish_for_later.md`); the coverage judge lane, the publish lane and control surface part 4 left switched off.
- **Code touched tonight is unreviewed** by his stop order; the standing rule says code is not clean until a review says so. He has not said what replaces review.
- **Spend:** system fell from 100% to 75% of its week (Fable 62%) between 6:55 and 10:21 PM PST; lukas 100%, steven 55% (Fable 37%). Five mods stay off on his 4:25 PM word; six biome mods and Graffiti stay HELD BY OWNER.
- **Second-wave owner calls** (owed `RIMMANDRAKE_BRING_SECOND_WAVE_OWNER_CALLS_ON_ONE_CARD`) were never carded this window.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. The Conductor's pointers each cite an open owed id too: file the act first (`rimflow file <ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; --check runs `owed.py check-pointers`. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_FIX_OPEN_CODEX_FINDINGS_ONE_AGENT_KEEPS_CONTEXT` — a Fable run (resumed 10:20 PM PST, unit ending 1795069192) lands its three finished designer_stage fixes, then fixes only findings an ordinary day reaches and lists the rest as polish; no reviews; NEXT: read its run-end report; confirm the three fixes landed and the clone is clean; do not relaunch it for the polish list (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN` — switched off (pipe off item) on his stop order; built parts are in; its last run found two defects that make the live launch-permit install unsafe (note 61c10cb848); NEXT: leave it off until the treadmill design is decided; the live install is owed under RIMMANDRAKE_INSTALL_PERMIT_DROPIN_LIVE_AFTER_CONTROL_FIXES_LAND (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_READ_ODD_RESULT_SHAPE_AS_BLIND_NOT_CRASH` — fix written as a patch in D:\ClaudeWork\rimmandrake\lane4, parked by rimflow wait until 2026-11-22 because worker.py may not land during the SteveDesktop soak; NEXT: after the soak ends apply the patch, run its acceptance test and the worker selftests, publish, close (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_RETIRE_COMBINED_SEA_DESIGN_TWO_SEAS_FOUND_WRONG` — a Fable run launched 10:17 PM PST (unit ending 1795069070) is removing or correcting the combined sea design; NEXT: read its report and the owner words it re-homed before telling him (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_WRITE_LAWS_FOR_EIGHT_FUZZ_FAMILIES_STILL_UNNAMED` — not touched by the Conductor this window; a helper lane claimed it; NEXT: run rimflow show on it and either relaunch it under the no-review addendum or put it back to proposed with a note (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)

- `RIMMANDRAKE_DESIGN_REVIEW_TREADMILL_FIX_COUNT_WAS_FLAT` — a Fable run (unit ending 1795069184) is drafting 01-design.md; NEXT: read the draft, then card its decisions to him (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING` — a Fable run (unit ending 1795069033) is reading the cut Forge, Rot and Stillsand files to the end; NEXT: read its DELETE-READY lines and tell him (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` — resumed 10:15 PM PST without reviews (unit ending 1795068941); NEXT: read its report; if a launch check went red, revert that landing first (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH` — resumed 10:15 PM PST without reviews; waiting-archive count 324, 236, 163, 88 and 123 rows deferred; NEXT: read its report against the pass mark of 0 deferred (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_UNPLACE_MACHINERY_HELPERS_FROM_MODS_SLOT_TAKEN` — decided 10:27 PM PST (record the mod at launch); a continuation that started before the decision holds the clone; NEXT: when it ends, launch briefs_20261118/unplace_helpers_record_mod_at_launch.md if the ticket is still open (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_RECONCILE_TWO_EXAM_RETAKE_TESTS_LEAF_VERSUS_FILE` — its killed run 1795061438 still reads running, so the clone is held and the relaunch was refused; NEXT: clear the stale run record the documented way, then launch briefs_20261118/_resume_reconcile-two-exam.md if present, else reconcile_two_exam_retake_tests.md plus the addendum (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_HOLD_REPAIR_LANES_UNTIL_HE_PICKS_SURVIVORS` — five lanes resumed on his "Don't hold for me"; coverage judge lane, publish lane and control part 4 stay off; NEXT: close this debt with the list of what resumed, or resume the three if the design says so (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_MEASURE_TWO_MORE_REVIEW_ROUNDS_BEFORE_ANY_FILTER` — overtaken: he stopped reviews and the flat count is measured; NEXT: close it citing 00-problem.md (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)
- `RIMMANDRAKE_CARD_REPAIR_RULES_WHEN_ROUND_SPLIT_IS_MEASURED` — the split is measured and told to him; the card now belongs to the design draft; NEXT: close it when the design card is put to him (owed `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN`)

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A handoff's "needs the owner" list is a snapshot: the last one said the gate order was "not answered" 17 minutes before he answered it by card, and the wake report copied it (filed: lessons, 20261119T031820Z).
- Ending a turn on "say go and I start" left the machine idle 90 minutes with him at the keyboard (filed: lessons, 20261119T062041Z).
- A run resumed after a spend stop read the cap from its own ticket's end-of-run note and trimmed its reading (see: RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED, fixed b08f107a1c).
- A second reader can mark a biome DELETE-READY while saying a roster was not read to the end: read the limits line, not only the verdict (see: RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING).
- "9, 11, 15 claims, rising" compared unlike counts; the same-basis series was 15, 11, 15 (see: design/specs/2026-11-18-review-growth-cycle/00-problem.md).
- `./publish` and `git commit` in the seat clone fail on a transient `.git/index.lock` and pass on retry (see: RIMMANDRAKE_RETRY_PUBLISH_ON_INDEX_LOCK_FAILED_TWICE_RUNNING).
- A killed or long-ended run can keep reading "running" or "in flight" and hold its clone (the slot-allocator run 1795046257 in `pipe show`, the reconcile run 1795061438) (see: RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE).
- Item names over 9 words are refused by `rimflow file` with only "the existing gate refused at the door" when the output is filtered: run `rimflow namecheck` first (see: skills/using-rimflow).

## Closed since the last handoff (115)

- `RIMMANDRAKE_REFUSE_UNREADABLE_OWNER_FEED_BLIND_IS_NO_REPLY` — 0d8c666b3097
- `RIMMANDRAKE_REWRITE_SCALD_SEA_DESIGN_READ_IN_FULL` — 29749224d14f
- `RIMMANDRAKE_BUILD_PACKET_BEFORE_SAVING_OPEN_RUN_PHANTOM_CHARGE` — 8992cdc87eb8
- `RIMMANDRAKE_REWRITE_GREY_SEA_DESIGN_READ_IN_FULL` — 8294b3d28724
- `RIMMANDRAKE_REWRITE_TWILIGHT_SEA_DESIGN_READ_IN_FULL` — ddc64f3dab17
- `RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD` — 087f5d91e625
- `RIMMANDRAKE_POINT_CONTROL_HOOKS_AT_RUN_CLONE_LAUNCHER_DELETED` — 16b922b388874a0491acadbf63bdb814d3bab684
- `RIMMANDRAKE_REWRITE_CHILL_SEA_DESIGN_READ_IN_FULL` — 18e4a66863f3
- `RIMMANDRAKE_RAISE_POOL_LINE_SIXTEEN_CLONES_NEVER_FIT_SEVENTY` — 12d3fb7100f147282d3aa6cd6634ba8a43f5c3c6
- `RIMMANDRAKE_REJECT_MALFORMED_RUN_FILES_SECOND_PASS_EXAM_SCENES` — 560c5dd3843a
- `RIMMANDRAKE_MATCH_ASK_REVIEWER_TO_AUTHOR_BY_AGENT_ID` — 0e7b0b57b99b
- `RIMMANDRAKE_HONOUR_CRITERIA_SUSPECT_IN_PROGRAM_RESULT_TOO` — f5fbaafde133
- `RIMMANDRAKE_ANCHOR_PIN_IN_CONCEPT_CLONE_NOT_DISPATCHER` — 73da0adc5ddf
- `RIMMANDRAKE_REFUSE_WAITING_RESULT_WITHOUT_FEED_BASELINE` — b5cbe7d26829
- `RIMMANDRAKE_NOTE_UNREADABLE_LIVE_PROOFS_AS_UNMEASURED` — b5cbe7d26829
- `RIMMANDRAKE_RECHECK_BLUEDESERT_TO_SLIME_CHOICES` — b71e54ede224
- `RIMMANDRAKE_CLOSE_FOUR_REPAIR_HOLES_CODEX_SECOND_LOOK_FOUND` — 92198f22dc9b
- `RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST` — 21221f031b350cb73c6e37216fd3f6b7f19d1395
- `RIMMANDRAKE_CLEAN_SEED_RECORD_WHEN_LANDING_TIMES_OUT` — eb05bc207356
- `RIMMANDRAKE_ROLL_BACK_AUTOLOCK_WHEN_RECORD_DIR_FAILS` — eb05bc207356
- `RIMMANDRAKE_RETRY_ROAD_BACK_FIXER_AFTER_TRANSIENT_LAUNCH_FAIL` — f9ebc4f931af
- `RIMMANDRAKE_RESUME_REPAIR_LANES_FOUR_STOPPED_FOR_ACCOUNT_SWITCH` — f9ebc4f931
- `RIMMANDRAKE_KEEP_LAUNCHED_UNIT_WHEN_LEDGER_AFTER_FAILS` — bcb440c84266
- `RIMMANDRAKE_BOOK_CODE_ON_LAUNCH_EXCEPTION_FRESH_FIX_SEEN` — bcb440c84266
- `RIMMANDRAKE_READ_FABLE_WEEKLY_METER_USAGE_LINE_NEVER_SHOWED` — c8793e7cc5f0bf5a4a9dc2093a433be99e6d8877
- `RIMMANDRAKE_WIRE_WRAPUP_RESTORE_ORPHANED_BY_RETIRED_TICK` — 491f1c8055126fe649b182381128706f96619f4c
- `RIMMANDRAKE_ORDER_UNTRIED_ROAD_BACK_ITEMS_BEFORE_SPENT_FAILURES` — 36915f0974f7
- `RIMMANDRAKE_GUARD_USAGE_POLL_WIPES_LATEST_ON_EMPTY_REGISTRY` — 92bd6967752624cc68e83001da42f3e18a6b16c5
- `RIMMANDRAKE_KEEP_CONDUCTOR_HOLD_ABOVE_COVERAGE_STOP_FIXERS` — 6732504a7241
- `RIMMANDRAKE_RETRY_FAILED_FIX_TICKET_LAUNCH_WHILE_PAUSED` — 6732504a7241
- `RIMMANDRAKE_KEEP_FILED_STEWARD_ITEM_ACROSS_LAUNCH_FAILURES` — 6732504a7241
- `RIMMANDRAKE_READ_WHOLE_LAUNCH_OUTPUT_FOR_TRANSIENT_FAULTS` — 6732504a7241
- `RIMMANDRAKE_CLEAN_SEED_RECORD_WHEN_LAND_CANNOT_START` — 6732504a7241
- `RIMMANDRAKE_ABORT_AUTOLOCK_WHEN_BACKUP_UNREADABLE` — 6732504a7241
- `RIMMANDRAKE_COUNT_NO_SLOT_FOR_AUTOLOCK_OR_REPIN_ACTS` — 6732504a7241
- `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS` — d953880e717f9bea48f487971e32ce4ef7186ca8
- `RIMMANDRAKE_FIX_ALARM_RECEIVER_TRUSTS_RETIRED_RELENTLESS_POOL` — 797a08f5e7a5384f8fc4b14ddc68c10af14897aa
- `RIMMANDRAKE_SHARE_GATE_RETRY_RULE_WITH_FIXER_SELECTORS` — a17db97b5a6f
- `RIMMANDRAKE_FIX_FOCUS_CAP_REFUSED_CLAIM_STILL_TAKES_LEASE` — 8716c3bcdd071304c9dba2e26302b18d1f4c0e4c
- `RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS` — a17db97b5a6f
- `RIMMANDRAKE_BIND_ESCALATION_TO_ITS_ORDER_NEWEST_TOOK_BLAME` — 32098a6e2cba
- `RIMMANDRAKE_CANCEL_ADMITTED_RUN_ON_UNIT_STOP_STILL_STARTED` — 32098a6e2cba
- `RIMMANDRAKE_END_SKIPPED_UNIT_RUN_LEFT_ADMITTED_FOREVER` — 32098a6e2cba
- `RIMMANDRAKE_FENCE_KILL_FAILED_CGROUP_READ_SAID_NOTHING_RAN` — 32098a6e2cba
- `RIMMANDRAKE_FIND_CLAUDE_SCOPE_ON_EMERGENCY_KILL_STORE_DOWN` — 32098a6e2cba
- `RIMMANDRAKE_READMIT_FAILED_LAUNCH_RELEASED_ROW_READ_UNREADABLE` — 32098a6e2cba
- `RIMMANDRAKE_SOUND_FAULT_ALARM_ON_METERED_RELEASE_TWO_MUTE` — 32098a6e2cba
- `RIMMANDRAKE_FIX_STOP_TEST_RACE_EMPTY_READ_COUNTED_ZERO` — 97c1ba43af2d
- `RIMMANDRAKE_CLOSE_STOP_FENCING_GAPS_CODEX_ROUND_TWO_FOUND` — dd34dd9e36b5
- `RIMMANDRAKE_PRINT_MEASUREMENT_REPORT_BESIDE_EVERY_GREEN_CHECK` — a6f66574d826
- `RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED` — cebbc5b2dd76
- `RIMMANDRAKE_PUBLISH_EVERY_DIRTY_SHARD_OWNER_FILES_WENT_UNSENT` — c38d4415aa15d5b9416815a78aef08c7231e407d
- `RIMMANDRAKE_SCOPE_LAND_REPLAY_TREE_AFTER_RENAME_MERGE` — cd3d6be6d8ce
- `RIMMANDRAKE_KEEP_AUTHOR_ON_LAND_REPLAY_COMMIT_TREE` — cd3d6be6d8ce
- `RIMMANDRAKE_LITERAL_LAND_PATHSPECS_AND_FETCH_TIP_CODEX_SAW` — cd3d6be6d8ce
- `RIMMANDRAKE_FINISH_ROLLBACK_WHEN_A_RESTORE_WRITE_FAILS` — e2aa419fe19254c001ebd0c6b3d9f60868b95ddd
- `RIMMANDRAKE_HARDEN_PUBLISH_PARK_RESTORE_RACE_CODEX_FOUND` — 3366de5aa45e
- `RIMMANDRAKE_HARDEN_ACCOUNT_USAGE_POLL_RACES_CODEX_FLAGGED` — dd37ba275875
- `RIMMANDRAKE_ATTRIBUTE_MANUAL_SWITCH_BY_LOG_NOT_OLD_MARKER` — e219f1e8729f
- `RIMMANDRAKE_KEEP_UNREADABLE_RECORD_WHEN_SEEDING_SAYS_NEVER` — c38fb7b10abb20de20f95f60a9b6c41815196f98
- `RIMMANDRAKE_SKIP_RESTOP_OF_STOPPED_FLEET_PUSH_EACH_PASS` — 4576205d06fe
- `RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED` — 9010e5074c262f2f0e8e4e5ffdd7bddb82fc9fd0
- `RIMMANDRAKE_FIX_KNOWN_RESULTS_AUDIT_NIGHTLY_SCOPED_TO_NOTHING` — ae36d62c2c5bc2f8225664718d4a412a209721bd
- `RIMMANDRAKE_COUNT_HAND_FIX_ON_UNBOOKED_ROAD_BACK_TICKET` — 0e9b7b1692d594d50cc0fe664fc37431c3dd77f1
- `RIMMANDRAKE_KEY_SETTINGS_EDITS_BY_OCCURRENCE_ABAB_LOST_ONE` — fbaa9266c6e491670abc916b36bb9dc0b2e6dead
- `RIMMANDRAKE_RECORD_DOOR_SKIP_FOUR_LANDINGS_LEFT_NO_TRACE` — 79b2a2169b17
- `RIMMANDRAKE_FIX_REAL_DIGEST_DETECTOR_BIG_NUMBER_COUNTS_GREW` — 7e79094c4e3c
- `RIMMANDRAKE_FIX_ASSERTCLOSE_NAN_THREE_OTHER_SELFTESTS` — 71c15213575d
- `RIMMANDRAKE_FIX_COVERAGE_JUDGE_TEN_FINDINGS_FIFTH_COUNT_CLEAN` — b8d12099e5eb631ca47ea689d873c63f52dee0ad
- `RIMMANDRAKE_READ_UNREADABLE_PID_AS_UNKNOWN_NOT_DEAD_YET` — dd2f57e81e99
- `RIMMANDRAKE_STOP_LANES_EASY_SPOT_BEFORE_STEVEN_HITS_LINE` — 52afce67f4
- `RIMMANDRAKE_FOLD_RECORDED_HAND_ACTS_AFTER_KNOWN_FAILS` — 4a23927267bc885f62087c30557f63a722b42b92
- `RIMMANDRAKE_SEED_SCENE_LOOK_CALIBRATION_BRIM_PIT_PAIR` — 86d35cdec854bba4ae0e2af45d46445d93393477
- `RIMMANDRAKE_OWN_VOIDED_TICK_RUNS_ARCHIVE_HID_THEM` — 8666586b8adbae55466ea70ce421a54f419cef73
- `RIMMANDRAKE_SPLIT_MANUAL_HAND_ACT_IDS_WITHIN_ONE_SECOND` — 8666586b8adbae55466ea70ce421a54f419cef73
- `RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO` — c180799371c76945dd29f35e2a5f9db52661b736
- `RIMMANDRAKE_HONOUR_DATED_WAIT_BEFORE_CONTINUING_TWICE_IDLE` — cb61feea75b3
- `RIMMANDRAKE_DECIDE_GUARDS_OWED_BY_LANDED_OLD_FIXES` — e1d8b84dcf5f
- `RIMMANDRAKE_RESTAGE_CSHARP_SUITES_FRESH_MTIME_STALE_FAULT_BINARY` — deff17d3ef29
- `RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS` — 018d405e54fe3916a7364bc529fe2d475aca492f
- `RIMMANDRAKE_ADD_PIPE_QUEUE_VERBS_QUEUE_VIEW_PRINTS_MEGABYTES` — 16ded1e1fb5f978368589246ce3d921a8ba0e4d7
- `RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS` — 1ba90a62fa3062e77b06db82967dc3759ed6810f
- `RIMMANDRAKE_REGISTER_EK_SELFTESTS_THIRTEEN_NO_TABLE_ENTRY_SAW` — 81af32921341
- `RIMMANDRAKE_FENCE_LAUNCH_IDENTITY_ONE_ID_TWO_PAYLOADS` — be673ed89530ff242fa64a9607ea98470c7746bd
- `RIMMANDRAKE_HARDEN_EMERGENCY_KILL_LOCK_FORK_AND_END_RACE` — be673ed89530ff242fa64a9607ea98470c7746bd
- `RIMMANDRAKE_KEEP_STOP_DEADLINES_TWO_TIMERS_ONE_NAME` — be673ed89530ff242fa64a9607ea98470c7746bd
- `RIMMANDRAKE_TIGHTEN_CENSUS_AND_P95_POOLED_HID_SLOW_VERB` — be673ed89530ff242fa64a9607ea98470c7746bd
- `RIMMANDRAKE_KEEP_FIRST_ADMISSION_ON_REFUSED_REPLACEMENT_ID_REUSE` — 53cb713db19de9e5fff02a005adbc7eea2241467
- `RIMMANDRAKE_BOOK_LOCKED_KILLS_BY_RUN_TIMERS_REAP_TWICE` — 53cb713db19de9e5fff02a005adbc7eea2241467
- `RIMMANDRAKE_TRACE_CENSUS_ALIASES_HALF_SECOND_READ_AS_ZERO` — 53cb713db19de9e5fff02a005adbc7eea2241467
- `RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_THREE_ELEVEN_UNTRIED` — 53cb713db19de9e5fff02a005adbc7eea2241467
- `RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER` — 6593d47a26356d3ff059f08bd013834c52838ce5
- `RIMMANDRAKE_SHARPEN_FLOWWORKS_VOLUME_LAW_ONE_DECILITRE_SLIPS_BY` — dbf76d554cd6dfbd05ea7bc5192dc6591350dcf3
- `RIMMANDRAKE_TRACE_ROLE_RUN_LOST_DONE_STRANDING_NOW_CAUGHT` — 3f9dc26cd5da1db1ffbf62d941a7e0b6a476acec
- `RIMMANDRAKE_RECHECK_SLEEPINGICE_TO_THEROT_CHOICES` — 5da7d5c5e21e
- `RIMMANDRAKE_RETIRE_RELENTLESS_COLLECTOR_READS_A_DEAD_STORE` — 66577f942c85405cdc31f170ac4c635b3a399c1a
- `RIMMANDRAKE_TEACH_EXAM_PACKET_PARTIAL_RETAKE_STEP_SEVEN_FORBIDS` — 84ef53b2315b
- `RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE` — 84ef53b2315b
- `RIMMANDRAKE_RETIRE_CIRCLING_WATCH_ONLY_THE_DEAD_TICK_CALLED` — 2406951ab1270a2fb699c143925f9a5fb5ff419e
- `RIMMANDRAKE_RECHECK_THESUMP_TO_WEEPINGSTONES_CHOICES` — 773d1f1411ce
- `RIMMANDRAKE_RECHECK_LANTERNDEEPS_TO_RUSTCATHEDRAL_CHOICES` — 2e9ddacd0472
- `RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_TWO_NINE_UNTRIED` — be673ed89530ff242fa64a9607ea98470c7746bd
- `RIMMANDRAKE_RELAUNCH_CUTOVER_CHECK_IF_RUN_ENDS_UNDECIDED` — a22c3e0bcf
- `RIMMANDRAKE_PLANT_FLOWWORKS_SETTLING_LAW_SHUTTLE_TRIPS_OTHERS` — 8fe7940f1f4c8ce9a0b9fdefbabce46962b039de
- `RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ` — d732c71852
- `RIMMANDRAKE_READ_ADVISORY_PRIOR_GAP_BEFORE_IT_BINDS_UNREAD` — 9aeaccc0a4e6
- `RIMMANDRAKE_REGISTER_UNLISTED_SELFTESTS_THREE_MODS_157_UNSEEN` — 257923658b21
- `RIMMANDRAKE_RECHECK_FEVERWOOD_GREENTIDE_ABYSS_CHOICES` — cab579074634
- `RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED` — b08f107a1c59
- `RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_NOTHING_AS_CODED` — eb691cf88b70b49c2b5f25015e971e77701b6b08
- `RIMMANDRAKE_FIX_SLOT_ALLOCATOR_OVERRIDE_AND_BURN_PICK` — done by verify, no close
- `RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED` — done by verify, no close
- `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS` — done by verify, no close
- `HANDOFF_RESTART_AUDIT_FILES_OWED` — done by verify, no close
- `RIMMANDRAKE_RECHECK_ADVANCE_CALIBRATION_TEST_PASSES_WITHOUT_ROW` — done by verify, no close

## Filed and still open (57) — the next seat's queue

- `RIMMANDRAKE_FEED_CLEANSE_OWNER_ANSWERS_SCALD_CARD_SAT_UNREAD` — The cleanse case for a mod does not name the owner's 2026-11-10 card answers when they sit under a differently named folder (TerminalBiomes: TheScaldF
- `RIMMANDRAKE_RECONCILE_POOL_CAPS_SIXTEEN_CLONES_OUTWEIGH_70_GB` — Pool caps disagree: 16 clones of ~4.5 GB outweigh the 70 GB cap
- `RIMMANDRAKE_CORRECT_FOUR_SEAS_GREY_CATCH_SAYS_THIRTEEN` — The four-seas design says the Grey Sea has thirteen catch kinds; his card of 2026-10-12 left four
- `RIMMANDRAKE_REWORD_REEFBACK_TEXT_PROMISES_A_LIT_GARDEN` — The reefback's shipped description promises 'the light of something else's garden' in a sea whose ban is no glow but its mark
- `RIMMANDRAKE_BUILD_GREY_LIT_GROUND_YIELDS_RULED_NEVER_FOUND` — Grey Sea: 'lit cells yield more' was ruled by card 2026-09-26 and no code for it was found
- `RIMMANDRAKE_GUARD_CONTROL_COPY_RETAINED_RULES_ONE_WORD_REVERSES` — designer_stage: control copy cannot reverse a retained rule
- `RIMMANDRAKE_RETIRE_COMBINED_SEA_DESIGN_TWO_SEAS_FOUND_WRONG` — When all four sea runs (Scald, Grey, Twilight, Chill) have ended: launch one Fable run that removes or corrects the Scald and Twilight sections of the
- `RIMMANDRAKE_TRIM_GSS_PROOF_SETTINGS_READS_THIRTY_SEVEN_PERCENT` — GSS proof_all spends 37% of its wall in jawa/mod_settings_fields reads
- `RIMMANDRAKE_PROVE_OBS_REPORT_ON_A_KEPT_GSS_RESULT` — Prove obs_report on a GSS run whose result is kept (bridge_run in the result, next live run)
- `RIMMANDRAKE_RECORD_SLACK_DELIVERY_MISSES_BEFORE_ANY_MACHINERY` — Record what went wrong in Slack's delivery before any machinery
- `RIMMANDRAKE_DELIVER_SLACK_THROUGH_STAGE_EIGHT_ITS_OWN_STAGES` — Deliver Gimme Some Slack through Stage 8 on its own stages
- `RIMMANDRAKE_WRITE_LAWS_FOR_EIGHT_FUZZ_FAMILIES_STILL_UNNAMED` — Eight matrix fuzz families have no written law yet
- `RIMMANDRAKE_INSTALL_VV_MATRIX_CLOCK_WRITTEN_NOT_RUNNING` — Install the rm-vv-matrix clock (written, not installed)
- `RIMMANDRAKE_MEND_ERA_SPLIT_SELFTEST_CALLS_REMOVED_REFUSAL` — An era-split selftest crashes: concept_tree.relentless_refusal was removed
- `RIMMANDRAKE_FIX_INCIDENT_CLOSES_ON_STALE_READING_THREE_FOUND` — incident.py, three pre-existing lifecycle defects a Codex full-file review found (unverified by a fixture yet): (a) ~L510 a stale status marks only op
- `RIMMANDRAKE_MEASURE_SLACK_LIVE_END_PARITY_COPY_AGAINST_GAME` — Gimme Some Slack live end: measure parity of the Python copy against the game
- `RIMMANDRAKE_COMPARE_SHARD_MODE_IN_LEDGER_EQUIVALENCE_CODEX_SAW` — seat_sync shard_upstream (~line 105) calls a ledger shard landed on identical lines without comparing file mode, so a local commit that only changes a
- `RIMMANDRAKE_GUARD_PARK_DROP_AGAINST_LATE_FD_SAVE` — seat_sync _drop_park_if_restored: a writer holding the parked file open can save through its old descriptor after the byte compare, and rmtree then de
- `RIMMANDRAKE_KEEP_STAGE_JSON_DESIGNERS_LEDGER_READS_HOMONYM_NAMED` — stage.json stays the Designer's; the mod ledger packet reads it as 'Designer step'
- `RIMMANDRAKE_LABEL_CONDUCTOR_OPENED_SCOPE_NOT_HIS_WORDS` — designer_stage: a scope the Conductor opens is stored opened_by_conductor, never opened_by_owner
- `RIMMANDRAKE_GUARD_PUBLISH_ROLLBACK_AGAINST_PEER_COMMIT` — publish.py: a red door check resets HEAD to <this run's commit>~1 unconditionally, so a plain git commit made by a peer during the checks is taken off
- `RIMMANDRAKE_CHECK_COMMITTED_TREE_NOT_DIRTY_WORKTREE_AT_DOOR` — publish.py: in a full clone the door checks run on the working tree, so an unstaged edit can make a check pass that the committed tree fails, and the 
- `RIMMANDRAKE_NAME_RECEIVER_FOR_SEAT_ALARMS_PENDING_WITH_NONE` — Since 797a08f5e7 new BENCH offline alarms (ops_watch, deadman, steward) stay PENDING with 'no receiver' instead of being filed to the Conductor queue.
- `RIMMANDRAKE_CHARGE_SHARED_OUTAGE_ONCE_FORTY_FIVE_DEATHS` — deadman + rimflow: one shared outage is one death, charged to the subject's host, not to every fix naming it
- `RIMMANDRAKE_REAP_SELFTEST_CHILD_ENDED_RUN_LEFT_HOLDING_CLONE` — A detached run that ends while a selftest it started is still running (run_selftests.py --_harness-child, selftest_second_game_mutants.py both times, 
- `RIMMANDRAKE_PREVIEW_THREE_GATES_READ_ONLY_FOR_LAUNCH_CHECKS` — read-only previews of the Designer open, coverage-judge and certify gates, for launch checks
- `RIMMANDRAKE_REFUSE_STAGE_THREE_BAR_READS_NO_BUILT_FILE` — maturation Stage 3 exit: a bar none of whose deciding tests reads a shipped file is not built
- `RIMMANDRAKE_ANNOTATE_FOLD_MEMORY_BESIDE_STANDING_WORK_COVER` — findings_fold: a memory decision annotates a standing cover decision instead of replacing it
- `RIMMANDRAKE_BRING_CODEX_FINDINGS_PROBLEM_OR_POLISH_NO_LEAN` — When the analyst's report codex_findings_problem_or_polish_20261118.md lands in the conductor folder: read it, bring him the table of the Codex-review
- `RIMMANDRAKE_READ_FOREIGN_DEF_NOT_FOUND_AS_LIST_FACT` — validation_core: a notFound def owned by a mod that is not loaded reads UNMEASURED, not FAIL
- `RIMMANDRAKE_TYPE_SIX_MORE_CONSUMABLES_READERS_IN_LIVE_LANES` — Slice 2 rest: six more consumables as typed accounts, readers in other lanes' files
- `RIMMANDRAKE_REPAIR_CONTINUE_STEP_FLAWS_CODEX_FOUND_SEVEN` — left_open_continue.py at cb61feea75, Codex full-file review (job consult-20261118-191545-757399-e717e0), older code: (1) a lane hand-off to a differen
- `RIMMANDRAKE_KEEP_UNJUDGED_CHAINS_WHEN_ONLY_CHAIN_FILTERS` — judge_cli --only-chain deletes the unselected chains from the saved results and turns their bars UNMEASURED
- `RIMMANDRAKE_RECONCILE_TWO_EXAM_RETAKE_TESTS_LEAF_VERSUS_FILE` — When the exam partial-retake builder reports: make one acceptance test of the two on the ticket (the six cases filed with it, and exam_retake_map_acce
- `RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE` — Six more void gaps Codex found: unknown results, --since on moved runs, unscanned books, void-mark retry, never-launched chains, loop ceiling
- `RIMMANDRAKE_REFUSE_MALFORMED_IDS_CLOSE_RUN_CRASHES_INSTEAD` — designer_stage close_run crashes on a non-string requirement or about id instead of rejecting
- `RIMMANDRAKE_REQUIRE_PASSING_ROW_TO_CLOSE_REPAIRED_SLOT` — coverage_judge: a repair slot closes with no passing checklist row for its ids, and coverage can sign
- `RIMMANDRAKE_REPOINT_EK_JOURNAL_JOLT_CHECKS_AFTER_PLAN_MOVE` — selftest_explosiveknockback_journal_jolt greps RM_MapComponent_Knockback.cs for throw rules that ffc3937ee7 moved into RM_KnockbackPlan.cs: 6 FAIL, 11
- `RIMMANDRAKE_CARD_FINDINGS_RULE_AFTER_HE_READS_THE_TABLE` — When he says he is ready: put the question card on how Codex-review findings are filed from now on (problem only with a named ordinary-day input and t
- `RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_FOUR_FIFTEEN_UNTRIED` — control.py: Codex review of the round-three fix, 15 claims (5 fixed, 10 to split)
- `RIMMANDRAKE_RETIRE_ARCHMAGI_LIVE_ROWS_DEAD_SINCE_NOV_SIX` — running_now.py's Archmagi live-testing tiles (PROOF ROWS BY RESULT, BUGS FOUND, the phone's LIVE TESTING line) read /home/mandrake/rm/relentless/live/
- `RIMMANDRAKE_RETIRE_JAM_CLASS_DETECTORS_NAMING_REMOVED_TARGETS` — rimflow/jam_classes.json's detector rows name OPS_RELENTLESS_UNSTICK, OPS_RELENTLESS_BOOKS_UNSTICK and relentless.* keys, all removed from ops_watch w
- `RIMMANDRAKE_NARROW_LAVA_LANDING_BURST_WHOLE_MAP_SCAN` — ShipShields: the lava-landing burst fires when lava is anywhere on the map, so every Forge landing would take it. Acceptance test: none, live-app beha
- `RIMMANDRAKE_REQUIRE_EXAM_EXPECT_VERDICT_WORD_492_ALREADY_DO` — exam_errors accepts a scenario expect with no accept/reject verdict word ("maybe: ..."), so a score has no defined right answer
- `RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE` — maturation.py: six flaws a Codex review found (unreadable spend file, UNMEASURED as 0, evidence folders kept across versions, owed scene bars, brief v
- `RIMMANDRAKE_SELECT_CALIBRATION_TEST_ON_REGISTRY_EDIT_JSON_UNSEEN` — The door never runs selftest_calibration_rows_current.py for a registry-only or evidence_gate_corpus.json change
- `RIMMANDRAKE_FIX_OPEN_CODEX_FINDINGS_ONE_AGENT_KEEPS_CONTEXT` — Fix every still-open ticket filed from the 2026-11-18 Codex code reviews (24 at the card: 11 minor, 12 polish, 1 unverified list) with ONE agent that 
- `RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING` — When the Sleeping Ice to Rot and Sump to Weeping Stones readers report: read the Forge, Rot, Webwork and Weeping Stones choices pages for readings cut
- `RIMMANDRAKE_MEASURE_TWO_MORE_REVIEW_ROUNDS_BEFORE_ANY_FILTER` — After two more Codex review rounds (tally: D:\ClaudeWork\rimmandrake\conductor\codex_review_rounds_tally.jsonl plus the lanes' tickets): bring him fin
- `RIMMANDRAKE_FIX_FLOWWORKS_FUZZ_FOUR_FLAWS_SINK_STILL_FLOAT` — Four older FlowWorks fuzz flaws Codex found reviewing the exact volume law: per-fluid and sink laws still float, probe counts and JSON
- `RIMMANDRAKE_DECIDE_ROT_BLASTPOD_GROWS_ONLY_ABOVE_FIFTY_DEGREES` — The Rot's wild blastpod (its chemfuel source) has a growth floor of 50 C on a biome whose maximum is +24 C. Acceptance test: none, an owner decision f
- `RIMMANDRAKE_RETRY_PUBLISH_ON_INDEX_LOCK_FAILED_TWICE_RUNNING` — ./publish in /home/mandrake/rm/bench failed three times tonight on 'Unable to create .git/index.lock: File exists' (once at commit 7:28 PM, twice in a
- `RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST` — control slices 2-4: Codex review, 20 findings (6 fixed, 14 to split)
- `RIMMANDRAKE_INSTALL_PERMIT_DROPIN_LIVE_AFTER_CONTROL_FIXES_LAND` — When the open control-store review claims (RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_FOUR_FIFTEEN_UNTRIED, 10 left) are fixed: install the permit drop-in
- `RIMMANDRAKE_CARD_REPAIR_RULES_WHEN_ROUND_SPLIT_IS_MEASURED` — When the analyst's report control_review_rounds_real_or_treadmill_20261118.md lands: read it and bring him one card with the per-round split (old code
- `RIMMANDRAKE_HOLD_REPAIR_LANES_UNTIL_HE_PICKS_SURVIVORS` — Nine repair runs were ordered to stop and write where they are at 8:24 PM PST 2026-11-18 (control acts up to ct_000055; each ticket switched off so no
- `RIMMANDRAKE_DESIGN_REVIEW_TREADMILL_FIX_COUNT_WAS_FLAT` — Draft the design that ends the review treadmill on pipeline code, from design/specs/2026-11-18-review-growth-cycle/00-problem.md: at least three genui

## Commits

```
09dd5f6d40 conversations: catch-up 1 record(s)
6befe1bc1c ledger: RIMMANDRAKE_RETIRE_COMBINED_SEA_DESIGN_TWO_SEAS_FOUND_WRONG note
01758b2c21 ledger: dispatch-cut ticket dropped as not needed; helper placement decided (record the mod at launch)
4e383de49e ledger: dispatch-cut ticket dropped as not needed; helper placement decided (record the mod at launch)
9e35e61381 FOUNDRY's identity file goes and set_agent_window.sh refuses the retired seat (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES)
88414efcf6 ledger: RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS clone bundled
db1fc49328 lesson: a stop order on one thing is not a hold on the rest; never idle waiting for a go
b5586cc8a2 conversations: catch-up 1 record(s)
17119cda0a ledger: detached run on RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS ended
8d88a8e512 ledger: RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_NOTHING_AS_CODED closed; lane 5 state
bfa6483b3c ledger: design ticket for the review treadmill fix; repair lanes resumed without review rounds on his "don't hold for me"
1137e68ac8 ledger: RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED clone bundled
eb691cf88b Item RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_NOTHING_AS_CODED.
81bd2a1618 conversations: catch-up 1 record(s)
6ca7f78b92 ledger: detached run on RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED ended
4e4a7a7b17 ledger: RIMMANDRAKE_HIDE_CAP_STOP_FROM_RESUMED_RUN_READER_TRIMMED closed
35f834c811 ledger: RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH note
1e6e9ac6fc ledger: DISPATCHER notes (1)
43f1bdde61 ledger: DISPATCHER notes (1)
2d0b052005 seat_dirt: land 1 safe path(s) left in the role clone Operations (conversation records, filed item prose, settled concept folders)
... 580 more: git log --oneline 21c0d2bd6f..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-17T19:16:24Z

Working tree clean apart from untracked `Transient/`.

