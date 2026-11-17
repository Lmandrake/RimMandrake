# BENCH_REBOOT_HANDOFF_202611170447 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611152326`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner is at his desk doing a live "rescue" sitting and it is working: keep it alive. FIRST ACT of the next window: re-arm the question watcher (a Monitor on `questions.md` in each showings folder, `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\` and `...\RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE\`); it died with this window. For each new `## Q` block: read it, LOOK at its picture, open the picture on his desktop (`powershell.exe Start-Process`), relay the question verbatim with what you saw, and append his answer verbatim to `answers.md` as `## A<n>` plus a `rimflow note --owner-said` on the item. Builders never wait; they read answers.md between steps. Gimme Some Slack is the top priority "at any cost" (owner 8:45 PM PST 2026-11-16) and he wants every further failure shown to him live.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
He is at the keyboard. Open with him, unanswered:
- PYRELANDS Q1 and Q2 (8:47 PM PST), picture opened on his desktop `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE\q1_flood_vs_line.png`. The rescue found the black-rain number is not the problem: in the real visit-1 saves one fire flooded 78% of the map in 4 days and grass fell 83% to 42%; fire against black rain has never run in game (that walk had the sky locked clear). It proposes wind-carried fire (each fire lights one cell downwind, so a lit line stays a line). Q1: narrow walking line with a greening trail, or a wall of fire sweeping the map weekly? Default: build the line, with a Mod Setting for vanilla spread. Q2: line width (9 cells, or about two dozen, the widest that does not summon its own rain) and whether the wind holds one direction per map or wanders. Default: keep 9 and 32, wind wanders. Relayed to him in the last reply of this window; his answer goes to answers.md verbatim.
- Told, and answered: Slack Q1 (order C, B, D), Q2 (A2 then C; bar exception granted), Q3 and Q5 (new whip approved, sharp kicks), bar wording accepted; Graffiti ugliness bar by card ("Look and stat agree").
- Reviews he has open in Typora: Fable's view `...\RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN\pipeline_view_from_fable.md`, GPT's review `D:\ClaudeWork\rimmandrake\conductor\gpt_review_pipeline_changes_20261116.md`. GPT's order of work (delivery first, finish one mod, one measurement report; no universal conflict stage yet) is my recommendation; he has not ruled on it.
- All approvals of the new whip are from OFFLINE animations; the in-game look is UNRUN.
- Spend ceiling released by hand for ExplosiveKnockback (about 11.2M weighted tokens, rel-d355a652e496); owed to his digest with the spend.
- The Slack and Pyrelands Fable runs have NO automatic spend stop (launched with budget 0 before the outside watchdog landed); watch their spend by hand and tell him in weighted tokens if large.
- Older, still unread by any Conductor: the nightly-reds report and the spend-unit card (previous handoff).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_BARS_LEFT` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_BARS_LEFT` and leave it to the tick, or close it if done
- `RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_BARS_LEFT` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_BARS_LEFT` and leave it to the tick, or close it if done
- `RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_LEFT` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_AUTOBUILD_PYRELANDS_ZERO_LEFT` and leave it to the tick, or close it if done
- `RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS` and leave it to the tick, or close it if done
- `RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK` and leave it to the tick, or close it if done
- `RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT` and leave it to the tick, or close it if done
- `RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF` and leave it to the tick, or close it if done
- `RIMMANDRAKE_DIAGNOSE_STEVE_WORLD_START_SIX_MODS_ONE_FAILURE` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_DIAGNOSE_STEVE_WORLD_START_SIX_MODS_ONE_FAILURE` and leave it to the tick, or close it if done
- `RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_ONE` — not started (an earlier launch failed at 5:05 AM); waits on a green certificate; NEXT: when the Slack certificate is green, let the pipeline launch visit 1 and point a watch window at it
- `RIMMANDRAKE_FINISH_SLACK_TONIGHT_TWO_DECIDERS_RED_AT_CERTIFICATE` — the Opus fixer ended (cap) after publishing 11643d9c82 and cd1fa27156; its certificate was refused 3 of 26 at 7:07 PM PST and its closing report is unread; superseded in practice by the Fable run; NEXT: read its out.json report, then close or supersede it by RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN
- `RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY` — the pipeline's or an earlier window's item, not touched this window; NEXT: run `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY` and leave it to the tick, or close it if done
- `RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP` — parent item, not touched this window; NEXT: `rimflow show` it and read the newest note before acting
- `RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN` — Fable run rm-detached-bench-rimmandrake-invent-slack-live-end-green-1794885421 live (session 0f924521-1b2a-4e01-8482-87e58a50c67f), port done, waiting on the certificate at 8:39 PM PST; NEXT: read its certificate result, tell him at once, and if green launch in-game visit 1 through the pipeline with a watch window (`wt.exe -w new --title ... wsl.exe -- python3 /mnt/d/ClaudeWork/rimmandrake/conductor/watch_run.py <ITEM> --back 40`); if the run ends short, resume it (`detached_helper.py launch ... --model fable --budget-usd 0 --resume <session>`)
- `RIMMANDRAKE_RELEASE_CONTAGION_JUDGE_ONE_LOOK_HIS_WORD_GIVEN` — owed item, parked: Contagion is one of the six biome mods he held 2026-11-16; NEXT: leave it parked (`rimflow wait`) until he lifts the Contagion hold
- `RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS` — opus run rm-detached-bench-rimmandrake-repin-graffiti-ugliness-bar-1794889468 live, carrying out his card (look and stat agree); NEXT: read its DETACHED RUN ENDED line in the Conductor log and tell him the new bar text and any other pinned-number bars it lists
- `RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE` — Fable Rescue run rm-detached-bench-rimmandrake-rescue-pyrelands-black-rain-1794889288 live, offline stage, Q1 and Q2 asked 8:47 PM PST and unanswered; NEXT: get his answer to Q1 and Q2 and append it verbatim to answers.md in its showings folder
- `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS` — run ended, item LEFT OPEN: cause was the 35M per-stage spend ceiling, status wording fixed (6f3ca6369f), ExplosiveKnockback released by hand and the tick then launched RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FIVE itself; Pyrelands is held from the tick by a 'kind hold' line in design/concepts/Pyrelands/journal.md; NEXT: file the item that makes a ceiling-paused mod raise a RAISE FIRST line to the Conductor, fold the hand act into it (`maturation_hands.py fold rel-d355a652e496 --item <ID>`), and lift the Pyrelands hold when its rescue ends
- `RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY` — filed with his words, no spec; three reviews exist (mine `conductor_pipeline_proposal.md`, Fable's `pipeline_view_from_fable.md`, GPT's `gpt_review_pipeline_changes_20261116.md`); `src/RimMandrake/rimflow/roles/fable_rescue.md` is v1 and does NOT yet carry Fable's ten amendments (sent to the Pyrelands run by answers.md) or GPT's cuts; NEXT: fold both reviews into fable_rescue.md once, write this item's spec with GPT's order (delivery first), and bring him the one-page result
- `RIMMANDRAKE_REPAIR_BAR_RULE_SELFTEST_RED_BLOCKS_PUBLISH` — opus fixer rm-detached-bench-rimmandrake-repair-bar-rule-selftest-red-1794890633 live; three builders published past this red test tonight; NEXT: read its DETACHED RUN ENDED line and report
- `RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FIVE` — launched by the tick itself at about 8:44 PM PST after the ceiling release; NEXT: leave it to the tick and tell him whether ExplosiveKnockback reached its in-game visit by itself
- `RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY` (second debt, no item yet) — the owner asked why a needs-owner hold (the Graffiti bar) was not carded at once; filing `RIMMANDRAKE_CARD_OWNER_HOLDS_FAST_GRAFFITI_BAR_SAT_SIX_HOURS` was refused at the door (gate A1); NEXT: run `rimflow namecheck` on that name, fix what it refuses, and file it for the Conductor with the acceptance test in its title

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Stopping a detached run by its .service name hangs 10 minutes while the agent keeps working; stop the claude-seat scope, snapshot the clone first (filed: lessons/20261117T044812Z-BENCH-stopping-detached-helper-by-its-service.md)
- A detached builder cannot hear the Conductor; give it questions.md/answers.md from the first brief and a Monitor in the window (filed: lessons/20261117T044812Z-BENCH-detached-helper-cannot-hear-conductor-mid.md)
- `claude --max-budget-usd` tells the agent its spend every turn (filed: lessons, 7852b14ceb; rule in CLAUDE.md)
- `maturation.py next` said "automatic" while the tick had the mod paused on the spend ceiling (see: 6f3ca6369f, fixed)
- `rimflow file --owner-said` refuses a quote that is a question; use --why and say whose call it was (see: skills/using-rimflow)

## Closed since the last handoff (163)

- `RIMMANDRAKE_STOP_ANSWERED_ASKS_RERAISED_THIRD_TIME_TO_HIM` — 526a10740789
- `RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT` — 77ba08dfecd1
- `RIMMANDRAKE_LAUNCH_FLOWWORKS_REALIGNMENT_PROMISED_NEVER_LAUNCHED` — 18ad3228eb
- `RIMMANDRAKE_FIX_DESIGNER_STALL_READING_BLIND_TO_CODEX_LANE` — e474d53b19a3eae0f095e31ce0934b633bfe481d
- `RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW` — c18e27a7a44e
- `RIMMANDRAKE_QUIET_LOCK_ALARM_ON_A_PUSH_THAT_WAITED` — 239be52bf9
- `RIMMANDRAKE_HUNT_BENCH_CLONE_WRITER_TWO_WAKES_READ_IT` — c6e103181b
- `RIMMANDRAKE_RECERTIFY_KNOCKBACK_TREE_BARRAGE_P99_HELD_AGAIN` — 0534f6c404bd93a1e2710dd66e3ea34ca1a990df
- `RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN` — 04182ca17826712ed2c796e74000055709f408e6
- `RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS` — 4cb69294d4c6
- `RIMMANDRAKE_CARRY_TOTAL_FIX_TALK_HE_ASKED_WHATS_MISSING` — 9db19a6f85
- `RIMMANDRAKE_FIX_PREFLIGHT_TIER_FULL_ITS_OWN_REPAIR_FAILS` — 5743a1dabbee
- `RIMMANDRAKE_FIX_PREFLIGHT_BARE_CUT_RED_ON_MAIN` — 6a41100464966dfc6f3c4e6b738aedb69d409194
- `RIMMANDRAKE_DESIGN_MOD_LEDGER_ENTRY_STANDARD_SMALL_SEARCHABLE` — d1f625a0c89f
- `RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE` — 2e6f7b431b6f81e56e1006d2e2df5fb48e2efaf1
- `RIMMANDRAKE_ADOPT_ENTRY_STANDARD_IN_MODLEDGER_FOURTEEN_OWED` — e7342388986d
- `RIMMANDRAKE_BACKFILL_SLACK_LEDGER_SHADOW_BESIDE_FLOWWORKS` — 62c18af00dbd
- `RIMMANDRAKE_START_PILOT_STAGE_RUNS_FROM_LEDGER_PACKET` — 773cc6fd6942
- `RIMMANDRAKE_LAND_EVERY_LEDGER_VIEW_CLOSED_WENT_STALE` — 304c84002db2
- `RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME` — 304c84002db2
- `RIMMANDRAKE_HOLD_KEPT_NEAR_DUPLICATE_DELETED_EVERY_OTHER_RUN` — d5b84f6592c2
- `RIMMANDRAKE_MINE_KNOCKBACK_CLOSED_TICKETS_NO_REFUTED_CAUSES` — 0d091ba95ed6
- `RIMMANDRAKE_LAND_HOLDER_GRANT_BEFORE_LAUNCH_CLONE_BLIND` — 0c763edd9f
- `RIMMANDRAKE_STRIP_HOLDER_WRITER_FROM_DOOR_TESTS_PUBLISH_REFUSED` — 0ed7ae5001
- `RIMMANDRAKE_ACCEPT_LEDGER_ONLY_TICKET_NAMES_THIRST_WAS_VALID` — e04d509dccb6
- `RIMMANDRAKE_REMINE_SLACK_TICKET_ONLY_ITEMS_HOLD_REFUTED_CAUSES` — 0805fd467504
- `RIMMANDRAKE_BACKFILL_FLOWWORKS_LEDGER_SHADOW_BESIDE_SLACK` — e8941312b149
- `RIMMANDRAKE_RUN_FINISH_WITHOUT_LAUNCHER_CLONE_HOLDER_LOST_RESULT` — 2c98b97e8602
- `RIMMANDRAKE_LET_HOLDER_TAKE_BRIDGE_ALL_ITEMS_NEED_GAME` — fa14c7d6b0d9
- `RIMMANDRAKE_BIND_CERTIFICATE_TO_OFFLINE_DECIDERS_NO_OP_PASSED` — 094cd380deb87403c1f3de7c6f697f04b1a7aeb5
- `RIMMANDRAKE_VALIDATE_CONTAGION_WALK_BARS_LIMB_LINE_WAITS` — db22459dac4dee2b9357109fb335c4f8866a5728
- `RIMMANDRAKE_REPAIR_BARRAGE_FRAME_CRITERION_BASELINE_FAILS_TOO` — 2a202dda96
- `RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_LOAD_FOLDERS_SAID_PIPES` — 396433f04a960f26f76fc51ce82faa387a17ae9b
- `RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_FIVE_FROM_PACKET` — 4ea72a1a30a733252389a7722fea0288d8b48459
- `RIMMANDRAKE_FINISH_FLOWWORKS_WALK_SCENE_HALF_THE_BAR_UNASKED` — f1e06be47a88
- `RIMMANDRAKE_PASS_BRIDGE_STATIC_CALL_INT64_POUR_LABELS_UNASKED` — 71eac62f2ff5
- `RIMMANDRAKE_REBUILD_FLOWWORKS_GARDEN_SCENE_MACHINES_NEVER_PIPED` — c6da40ed34
- `RIMMANDRAKE_REBUILD_FLOWWORKS_HOSE_SCENE_PUMP_HAD_NO_SOURCE` — b3bfaa7038
- `RIMMANDRAKE_REBUILD_FLOWWORKS_PITTRAP_SCENE_STOPPED_BY_OWN_RAID` — e9f2f50fd215
- `RIMMANDRAKE_REBUILD_FLOWWORKS_SOURCE_PAYS_SCENE_POND_NEVER_THERE` — e9f2f50fd215
- `RIMMANDRAKE_REBUILD_FLOWWORKS_TRENCH_SCENE_READ_LID_PROOF` — e9f2f50fd215
- `RIMMANDRAKE_REPAIR_FLOWWORKS_OL_SHADOW_JUDGE_PRESUMED_STALE` — e9f2f50fd215
- `RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED` — 1b15a9ba4ba6
- `RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT` — f03d8d4f4a
- `RIMMANDRAKE_MOVE_PIT_FETCH_CORPSE_OFF_RIM_TOUCHED_ABOVE` — f03d8d4f4a
- `RIMMANDRAKE_REPAIR_SLACK_LEDGER_CITATIONS_FOUR_POINT_NOWHERE` — 12c5a5757348
- `RIMMANDRAKE_RENEW_HOLDER_LEASE_BRIEF_NEVER_SAID_HOW` — 5ad5eb83ac
- `RIMMANDRAKE_STUB_HOLDER_RESUME_READINESS_REAL_LEDGER_LEAKED` — 9117cdc73f
- `RIMMANDRAKE_ROUTE_HELD_FIRST_AWAY_FOUR_HOLDS_NO_FAULT` — 910cd10c75
- `RIMMANDRAKE_FIX_CONTAGION_COVERAGE_GAPS_TWENTY_FIVE_ALL_SOUND` — 2f48bdaa28c28b2f0ed6ee0a08f4733db0061bbd
- `RIMMANDRAKE_FIT_PACKET_FLOOR_FLOWWORKS_246_FINDINGS_OVER_LINE` — 3d4070ef04cfc75b764767d1764c85aae4d3a7f9
- `RIMMANDRAKE_REFUSE_PILOT_LAUNCH_ON_LIVE_RUN_TWO_JUDGES` — 3d4070ef04cfc75b764767d1764c85aae4d3a7f9
- `RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE` — 3d4070ef04cfc75b764767d1764c85aae4d3a7f9
- `RIMMANDRAKE_GUARD_PILOT_LAUNCH_TWO_JUDGES_ONE_CYCLE` — f4e796daccda
- `RIMMANDRAKE_ORDER_REMINE_LINES_KNOCKBACK_STAGE_READ_BACKWARDS` — 837df071d3
- `RIMMANDRAKE_LAUNCH_THREE_MINING_BACKFILLS_THEN_HOLDERS_AT_ONCE` — 38e9c9a213
- `RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_SIX_TESTS_FIRST` — 290ce0c73616414b12b92c84bae70fb8aff9f065
- `RIMMANDRAKE_COMPLETE_GIMMESOMESLACK_CYCLE_SIX_RECORD_NO` — e3dc2246c1
- `RIMMANDRAKE_RENEW_LEASE_TWICE_SECOND_SAID_ALREADY` — ca4537f20d
- `RIMMANDRAKE_CONFIRM_GIMMESOMESLACK_CYCLE_SIX_EXIT_MET` — 7d7572ac2377
- `RIMMANDRAKE_SPARE_LIVE_CLONE_FROM_DEBRIS_FIFTH_RUN_SAME` — 195a94ec9695
- `RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED` — 0459550b0c
- `RIMMANDRAKE_BUILD_FLOWWORKS_THREE_RED_OFFLINE_TESTS_NOBODY_OWED` — 8e4a9cd5e482
- `RIMMANDRAKE_RESUME_CERTIFICATE_RERUN_KILLED_AFTER_THIRTY_EIGHT` — 7bdce8e4b76c
- `DESIGNER_STAGE3_RESOLVE_ARTIFACTS_IN_CONCEPT_CLONE` — 45e3f2d4c7e65f7489397b60d1119c041c01843e
- `RIMMANDRAKE_FIX_DISPATCH_VIEWS_LANDED_BLIND_TO_PEER_SHARDS` — 7b1ff1b4d545
- `RIMMANDRAKE_ADVANCE_FLOWWORKS_PAST_OFFLINE_BUILD` — 41e277c3e7ac
- `RIMMANDRAKE_SHOW_ADVISORY_COVERAGE_WITHOUT_OWNER_FORK` — ae8b1f356bca89b2c3fe8535c77833dbcf2f5a41
- `RIMMANDRAKE_IGNORE_DESIGNER_CAUSAL_LINKS_AS_OWNER_INPUT` — 699f40eeea3783fbfea806478348fda64844edfb
- `RIMMANDRAKE_READ_CLEARED_RED_KEYS_SANE_HELD_NIGHTLY_STUCK` — 19ac0af54ea5
- `RIMMANDRAKE_ASK_WALK_FRAME_BAR_EIGHTY_WITHOUT_MOD` — 34f958db99
- `RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD` — 6165b28d4a79057362e5810ecb332b1b1b96cadd
- `RIMMANDRAKE_LAND_DESIGNER_WORK_HARVEST_STRANDED_TWICE` — d9d0678b58729e381faa89ad2b2c3b00cf8f2da3
- `RIMMANDRAKE_RETAKE_GELATINOUSSLIME_EXAM_FAILING_ITS_GATE` — 7e64892643f03b946590d021846c864c3e231608
- `RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED` — d6ab2b663274
- `RIMMANDRAKE_VALIDATE_FEVERWOOD_NEW_WALK_BARS` — 95c5d7512e159cb0a0fba772381a49e64163eed1
- `RIMMANDRAKE_STAGE_SLACK_REVIEW_MAP_HIS_EYES_BEFORE_JUDGES` — 1833dceb4c67
- `RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO` — 99aa8bdc4c5a
- `RIMMANDRAKE_CHECK_SLACK_BUILDER_AGAINST_WALK_FINDS_NEVER_SEEN` — 9c8ce39b77
- `RIMMANDRAKE_REVIVE_V3_VERDICT_TIMER_PRUNED_NEVER_ENABLED` — a667ca7e17
- `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS` — 34237790bd8d
- `RIMMANDRAKE_FREE_DEAD_OWNER_DRIVER_LOCK_BLOCKS_EVERY_TAKE` — 9d0451b34a74
- `RIMMANDRAKE_APPLY_CONTAGION_JUDGE_FIXES_EIGHT_REFUSALS_HALTED` — 2157db120fc6349a767c5df14206f970dfe4553f
- `RIMMANDRAKE_LOCK_GSS_SELFTEST_STAGE_SHARED_BY_EVERY_CLONE` — 2a74400398d0ff25f295f30940166cffce89311f
- `RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN` — 34b6b83c05264165739964b521e31f1f3a0466e4
- `RIMMANDRAKE_SKIP_LANDED_TWINS_PUBLISH_REPLAY_RESURRECTS_FILES` — 657a2a262a847207ba4bb62a69c656268012ebe5
- `RIMMANDRAKE_FREE_GRANT_FROM_REPIN_ON_UNLOCKED_CONCEPT` — 5880cdb533
- `RIMMANDRAKE_RESCOPE_CONTAGION_BARS_BY_RULING_YIELDS_NOT_BARS` — f0ad915d15
- `RIMMANDRAKE_CHECK_ADVISORY_VERDICT_STILL_RAN_DESIGNER_TWICE` — 3dad30ceee43
- `DESIGNER_GAPJUDGE_FIX_ONE_BATCH_PER_ROUND` — 579eb0616889
- `RIMMANDRAKE_ROUTE_STUB_JOINS_PROBE_PAST_REFUSED_SINGLE_SET` — 8a645a7c337e
- `RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS` — 579eb0616889
- `RIMMANDRAKE_LOCK_PYRELANDS_TWO_LEAVES_THE_TABLE_MAKER_REFUSES` — f951af41a352
- `RIMMANDRAKE_FIX_PYRELANDS_BURN_COST_TEST_RED_TWICE_TODAY` — f951af41a352
- `RIMMANDRAKE_KEEP_PYRELANDS_TABLE_ADDITIONS_THE_MAKER_ERASES` — f951af41a352
- `RIMMANDRAKE_FIX_SWAY_STAGER_WSL_PATH_DIED_AFTER_SAVING` — a4af69ccff2a
- `RIMMANDRAKE_FIX_FLOWWORKS_CROP_WEEK_FOLLOWS_PULSE_SLIDER` — 4b33b22f003b1c7cd76acc19a2e028d1bcfd4b67
- `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_CALLER_CROP_AGE_UNSEEN` — 4b33b22f003b1c7cd76acc19a2e028d1bcfd4b67
- `RIMMANDRAKE_PIN_FLOWWORKS_DRILL_CALLER_CHARGE_UNSEEN` — 4b33b22f003b1c7cd76acc19a2e028d1bcfd4b67
- `RIMMANDRAKE_PIN_FLOWWORKS_THIRST_CALLER_FALL_UNSEEN` — 4b33b22f003b1c7cd76acc19a2e028d1bcfd4b67
- `RIMMANDRAKE_PIN_FLOWWORKS_COATING_LAWS_MISS_DEAD_TICK` — 4b33b22f003b1c7cd76acc19a2e028d1bcfd4b67
- `RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE_TWO_TESTS_FIRST` — bb7cffa31fb132467e0a091ae600d1859fb3c7a5
- `RIMMANDRAKE_IGNORE_SEAT_QUEUES_AND_MODSET_SNAPSHOTS` — 71edba5965a2c3a4388291722686fa810140bc34
- `RIMMANDRAKE_STOP_RELENTLESS_SELFTEST_LOGGING_FAKE_CLONE_FAILURES` — ac6204c621704ddea4f740cefa0ec5c2d0d4a60f
- `RIMMANDRAKE_FLUSH_PUBLISH_OUTPUT_SO_TAIL_SHOWS_REFUSAL` — 366ff009a61017e86fbe04c0567faa2b6ac10c3b
- `RIMMANDRAKE_REFUSE_UNINDEXED_SHARD_NOT_CRASH_SEAT_SYNC` — 366ff009a61017e86fbe04c0567faa2b6ac10c3b
- `RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR` — 7cb1943de5
- `RIMMANDRAKE_ADVANCE_LEANINGSCRUB_LOCKED_VERSION_TO` — 73f1aa36c919939d33d01db2506a81cab3dd5fe9
- `RIMMANDRAKE_ROUTE_FLOWWORKS_CYCLE_TWO_FAILURES_BACK` — aefabaf6023c305ce9400b5bfd5422152e73dbc2
- `RIMMANDRAKE_PIN_BARS_MD_WHEN_PIPELINE_LOCKS_A_MOD` — 16517ae351ddd5344cc968de9e8e59e4ddd86b3c
- `RIMMANDRAKE_STEWARD_LEANINGSCRUB_PREFLIGHT_STAGE` — c4fe2ae62aed3b37f239a4c69b041d7dd809d935
- `RIMMANDRAKE_ALLOW_STEWARD_EXAM_RETAKE_ITS_OWN_FIVE_READERS` — 153991c96708c37bd508f3a4da18adf183120565
- `RIMMANDRAKE_UNPIN_RETAKE_DONE_FROM_A_RESULT_NEVER_WRITTEN` — 153991c96708c37bd508f3a4da18adf183120565
- `RIMMANDRAKE_RETAKE_CONTAGION_EXAM_FAILING_ITS_GATE` — 153991c96708c37bd508f3a4da18adf183120565
- `RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES` — 773b9baea39f
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_LEFT` — 5edd112f02f0
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_BARS_LEFT` — a1bf3326632dbf9418438640b5bb44af80bdae5b
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_NINETY_FIVE_BARS_LEFT` — d74f38ee955d8a58d6698d1f3a9f3ff476e291bb
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_EIGHTY_SIX_BARS_LEFT` — 430586f54e
- `RIMMANDRAKE_ROUTE_EXPLOSIVEKNOCKBACK_VISIT_THREE` — f4c7abe83886
- `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_REACH_THE_KERNEL` — 96941bfa43e903180fedad8a5099edb6237ad72b
- `RIMMANDRAKE_PIN_FLOWWORKS_CROP_DELAY_TEXT_FOLLOWS_PULSE` — 96941bfa43e903180fedad8a5099edb6237ad72b
- `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_DELAY_UP_AND_DRYING_CAP` — 96941bfa43e903180fedad8a5099edb6237ad72b
- `RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_KEEPS_DRINKERS_RESERVE` — 96941bfa43e903180fedad8a5099edb6237ad72b
- `RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE_THREE_TESTS_FIRST` — 5533ed8e8e9af830e43c08a5bafdb7b1dac29370
- `RIMMANDRAKE_ADVANCE_PYRELANDS_PAST_OFFLINE_BUILD_RUN_TWO` — 4d926284c87f
- `RIMMANDRAKE_REPIN_FLOWWORKS_PIT_CENSUS_AFTER_GSS_DROPPED_RIPPLE` — d0d33973116a56ea96e87153e1d5c95a6893b402
- `RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING` — a84613e77e
- `RIMMANDRAKE_REASK_PACE_AT_FORTY_PERCENT_HE_CHOSE_SPEED` — cd5dedb8f1
- `RIMMANDRAKE_SHOW_SLACK_FIXES_LIVE_WHEN_BUILDERS_END` — cd5dedb8f1
- `RIMMANDRAKE_ROUTE_FLOWWORKS_CYCLE_THREE_FAILURES_BACK` — a05f0a3b6e808a6700141a258d52d890586af98d
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_SEVENTY_EIGHT_BARS_LEFT` — 3387bc2292fd
- `RIMMANDRAKE_RERUN_STALE_CERTIFICATE_STAMPS_NOBODY_OWNS_IT` — c869468d456e
- `RIMMANDRAKE_STOP_EK_PILOT_KILLING_BOTH_GAMES_BY_NAME` — 09c170081ca28e89a393064eda919a2a701a69ec
- `RIMMANDRAKE_PASS_GAME_B_COMPUTE_FLAG_SAME_GPU` — 09c170081ca28e89a393064eda919a2a701a69ec
- `RIMMANDRAKE_SCRIPT_GRAFFITI_WALL_AND_ART_SCENES_DRAFTS_DIED` — 5d1a1ec45a84
- `RIMMANDRAKE_ALIGN_LANE_FRAME_ROW_TO_P99_STILL_WORST` — ce0b84ea6d3725e210e0d9e1ac14493ba0250cb4
- `RIMMANDRAKE_BREAK_COVER_UNDER_LANDING_STACK_STILL_WHOLE` — a9eedde493148be8b96d3540fa5a39e42d2e9626
- `RIMMANDRAKE_ADVANCE_GRAFFITI_PAST_OFFLINE_BUILD` — 5f1a43837ec6743b40b563e11ec3dff600349cc7
- `RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD` — 91f2bca5e2
- `RIMMANDRAKE_ADVANCE_EXPLOSIVEKNOCKBACK_PAST_OFFLINE_RUN_TWO` — 040f55f95e0140a36c55ad26834f1e81b6b99343
- `RIMMANDRAKE_TRIAL_SECOND_GAME_ON_ARCHMAGI_STEAM_LINK_UNTESTED` — 09c170081ca28e89a393064eda919a2a701a69ec
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_SEVENTY_BARS_LEFT` — 4802e0aca0b3f8c5ab0266b600a2a0842271d4af
- `RIMMANDRAKE_HARDEN_PYRE_GATE_SWEEP_BLIND_TO_OWN_WIRING` — b7b77c929e8c1782c07ee2714d7b62082f9cd7a2
- `RIMMANDRAKE_HARDEN_PYRE_SWEEP_SLIDER_MAY_HIDE_ITS_DEFAULT` — b7b77c929e8c1782c07ee2714d7b62082f9cd7a2
- `RIMMANDRAKE_HARDEN_PYRE_ENGINEERED_FACT_PASSES_A_NEGATION` — b7b77c929e8c1782c07ee2714d7b62082f9cd7a2
- `RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_TWO_TESTS_FIRST` — 7293b1d92565a8309723c9d765de13b62deccd2a
- `RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_ONE_TESTS_FIRST` — 67b0c4cacd896da5af7d2ba36f84686e1f29d06e
- `RIMMANDRAKE_ROUTE_PYRELANDS_CYCLE_TWO_FAILURES_BACK` — 26c6f53375c0c7b5a6e19eef549d9644e4670594
- `RIMMANDRAKE_PASS_BLIND_EXIT_ZERO_OFFLINE_BARS_GRAFFITI_STUCK` — e4d70a782efd5fd50bd43fcf201e82759e751af6
- `RIMMANDRAKE_ROUTE_GRAFFITI_CYCLE_ONE_FAILURES_BACK` — e4d70a782efd5fd50bd43fcf201e82759e751af6
- `RIMMANDRAKE_DIAGNOSE_PIPELINE_STALLS_NOTHING_ADVANCES_BY_ITSELF` — a046614c02a26bf0631867006304a4e22024997b
- `RIMMANDRAKE_RESTORE_KILLED_MUTANTS_SIGKILL_SKIPS_FINALLY` — ce417b9d88
- `RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS` — eb5be2de53
- `RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_FIFTY_NINE_BARS_LEFT` — 6702894be7f71fcba0991e31b77fb6f86c19ceb1
- `RIMMANDRAKE_PREPARE_SLACK_WATCHED_SITTING_HE_SEES_THE_JUDGE` — e57e79fe77
- `RIMMANDRAKE_PROVE_SPEND_BLIND_DETACHED_RUN_ONE_TINY_TURN` — 76dd23d59d
- `RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN` — 76dd23d59d
- `RIMMANDRAKE_CONSULT_GPT_ON_PIPELINE_CHANGES_AFTER_FABLE_ANSWERS` — 288d999968
- `RIMMANDRAKE_ACCEPT_EXAM_SESSIONS_UUIDS_ARE_IDENTITIES` — done by verify, no close
- `RIMMANDRAKE_PURGE_V3_VERDICT_RULE_RETIRED_BY_CARD_UNRUN` — done by verify, no close
- `RIMMANDRAKE_ROUTE_LIVE_ONLY_DECIDER_STAGE_THREE_NO_ROAD` — done by verify, no close
- `RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_STAYS` — done by verify, no close

## Filed and still open (113) — the next seat's queue

- `RIMMANDRAKE_TRIM_DISPATCH_DECIDE_CUT_TWENTY_SEVEN_TIMES` — Trim the Dispatcher's decide inside its beat (27 observe cuts, 2 beat_starved in 24 h)
- `SCRUB_PROVE_ROUTES_AND_SAVED_JOURNEY` — LeaningScrub: implement route observation, scoped-order controls and real saved-colony/reordered journey acceptance
- `SCRUB_PROVE_VINE_FORMS_AND_CRAFT` — LeaningScrub: implement complete vine, claim-migration and useful premium fuel proof scenes with exact recovery
- `SCRUB_PROVE_ECOLOGY_AND_TREE_PRODUCTS` — LeaningScrub: implement independent ecology, tree products and owner-attended motion acceptance scenes
- `SCRUB_PROVE_WIND_FIRE_AND_RITUAL` — LeaningScrub: implement wind, evidence observation, base-herd and actual ritual proof scenes
- `SCRUB_PROVE_SETTINGS_AND_COMPATIBILITY` — LeaningScrub: implement common recovery/log/tier harness, complete settings, technology, aliases and floor proof scenes
- `RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF` — ExplosiveKnockback: retake the Stage 4 Cold Reader exam against the re-certified tree (barrage p99 rewording); repin left stage 4 stale by its own rul
- `RIMMANDRAKE_AMEND_SPINE_DOOR_CLAUSE_TICKET_THREE_MUST_BREAK` — Ticket 1's acceptance test forbids the door wiring ticket 3's test requires: for a neutral fixer
- `RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF` — Deep design pass: fuse long-term mod holders with the Maturation Pipeline (pipeline as the holder's checklist; one monotonic per-mod ledger; blind jud
- `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` — Cut the three pilot mods over to their mod ledgers, old stores archived, writers redirected
- `RIMMANDRAKE_LIST_MODLEDGER_DELETIONS_ON_DAILY_DIGEST` — Put the mod-ledger deletion monitor's flagged rows on the Conductor's daily digest
- `RIMMANDRAKE_ADMIT_TEN_WORD_FAULT_ID_INTO_KNOCKBACK_LEDGER` — Explosive Knockback's 10-word blind fault id fails the finding namecheck, so the standard backfill leaves it out. Acceptance test: modledger_backfill.
- `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` — Live half: kill a real resumed EK holder run; the next launch reconciles and resumes
- `FEVERWOOD_PROOF_OBSERVATION_AND_RECOVERY` — FeverWood: independent state observations and recoverable proof scenes
- `FEVERWOOD_BRANCH_MUD_AND_LIVING_WOOD` — FeverWood: prove branch work and deliver the documented mud and living galleries
- `FEVERWOOD_WATER_STATE_AND_WARNING_CONTRACTS` — FeverWood: reconcile pool memory, shared strikes, warnings and adult quiet
- `FEVERWOOD_CAPTIVE_ESTABLISHMENT_AND_RETURN` — FeverWood: delayed pool establishment and complete captive return journeys
- `FEVERWOOD_LURE_AND_REACTIVE_HIVE_JOURNEYS` — FeverWood: real living bait, separated fronts and generated hive journeys
- `FEVERWOOD_CROWN_ECOLOGY_AND_OIL_JOURNEYS` — FeverWood: functional crown ecology and normal oil harvest and ignition
- `FEVERWOOD_SUPPORTED_CHECKOUT_AND_FLOOR` — FeverWood: supported composition, settings, geometry heat and floor checkout
- `RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_EIGHT_OF_TWENTY` — Fix the ticket miner along the independent judge's path to pass (verdict D:\ClaudeWork\rimmandrake\conductor\mining_samples\GimmeSomeSlack.judge.json:
- `RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER` — FlowWorks ProofSubmerge reports no shadow draw queue: OL_no_surface_shadow_under_sheet reads BLOCKED ON HOOK
- `RIMMANDRAKE_SPLIT_GSS_DLL_HOSE_DRAW_ORDER_SHARED_TABLE` — Polish: the shipped GSS DLL carries hose-named draw-order members (HoseQueue, LayerHose ...) compiled in from _Shared/SlackGeometry/DrawOrder.cs
- `RIMMANDRAKE_GRANT_BLIND_JUDGE_A_JUDGE_WRITER_VERDICTS_REFUSED` — A blind-judge run launched as HOLDER cannot write finding.verified/finding.open, so a blind cycle's verdicts never reach the mod ledger
- `RIMMANDRAKE_DRAW_CONTAGION_FLIPBOOKS_TWO_FLYERS_HALF_DRAWN` — Contagion: Blisterfloat and Gorekite need whole-body flying flip-books (Skinflap and Sparkleech have them)
- `RIMMANDRAKE_VETO_DUPLICATE_PICKUP_ACROSS_SEALED_PIT_DROPS_HAUL` — FlowWorks: vanilla's duplicate pickup retargets a haul at a stack in a sealed pit (raised ladder) within 8 cells; the path errors, the carried stack i
- `RIMMANDRAKE_MIRROR_KNOCKBACK_STAGE_LEDGER_SAYS_OFFLINE_BUILD` — ExplosiveKnockback's mod ledger says stage offline_build while its stage record says in_game, so its backfill acceptance fails and pilot_ledger() is f
- `RIMMANDRAKE_REPAIR_INCIDENT_SELFTEST_RED_TWO_ON_MAIN` — selftest_incident red on main: ops_watch.py:1084/1090 alarm keys unreadable by census; role_launch codex_stop alarm unreviewed
- `RIMMANDRAKE_BUILD_CONTAGION_REPULSOR_WARNING_NAMES_WHOLE_MAP` — Contagion Repulsor whole-map warning before warmup (approved per d_efa_q04; CompCloudRepulsor.cs has no warning or confirm text, measured 2026-11-16 b
- `RIMMANDRAKE_BUILD_CONTAGION_TOUCHED_TRANSITION_MESSAGE_SENT_ONCE` — Contagion-touched: one transition message when the progression reaches active change (RM_ContagionTouched.cs sends only the 'Contagion mutation:' lett
- `RIMMANDRAKE_RETIRE_CONTAGION_BIOME_SCORER_WORLD_IS_FROZEN` — Contagion legacy_placement_worker (scope out by the no-worldgen ruling): RM_BiomeWorker_Contagion.GetScore returns baseScore at the shipped biomeRarit
- `RIMMANDRAKE_COVER_FLOWWORKS_REVIEW_MAP_THIRTY_NINE_STILL_UNSHOWN` — FlowWorks selftest_review_map.py is red on main: 43 inventory items match no FEATURES rule in review_map_coverage.py (39 after this run covered 5)
- `RIMMANDRAKE_SEAL_JUDGE_SHARD_FROM_SYNCED_CLONE_SEALED_EMPTY` — modledger.seal sealed JUDGE.judge-1794822890 (Gimme Some Slack blind cycle 6) as 0 lines at 10:25Z from a Dispatch clone that lacked the shard; origin
- `RIMMANDRAKE_GUARD_GSS_NOHOSE_FLEXIBLE_PIPES_CLAUSE_UNMUTATED` — Polish (GSS 0.1.0 blind cycle 6): T_NO_HOSE's 'flexible pipes' clause has no self-mutant; dropping it stays green
- `RIMMANDRAKE_SCAN_GSS_ABOUT_TEXT_HOSE_CLAIMS_UNREAD` — Polish (GSS 0.1.0 blind cycle 6): T_NO_HOSE does not read About.xml; a hose claim there stays green
- `RIMMANDRAKE_SEE_GSS_DLL_HOSE_NAMES_HIDDEN_IN_TAILS` — Polish (GSS 0.1.0 blind cycle 6): T_NO_HOSE blind to tail-shared DLL names (LayParams.Hose, CordKind.Hose) and to C# identifiers
- `RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK` — Polish (GSS 0.1.0 blind cycle 6): an orphaned SelfTest dotnet.exe locks the staging DLL; next offline run goes red
- `STILLSAND_ACCEPTANCE_SCENES_ASSERT_CONTROL_RECOVER` — Implement Stillsand stage-3 script scenes with asserted starts, discriminating controls, honest observers and exact interrupted-state recovery
- `STILLSAND_PREY_SELECTION_EXCLUDES_WATER_RANKING` — Replace rejected Stillsand water-ranked prey selection while preserving giant hunt, physical eligibility, droid immunity and wet-thumper draw
- `RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD` — Dispatch tick launches runs from a clone 51 min behind origin (filed a ghost steward run)
- `RIMMANDRAKE_FILL_HEAVY_LOCKER_REAL_MASS_ESTIMATE_FELL_SHORT` — ExplosiveKnockback proof: sc_closed_containers' heavy locker is filled by estimated gun mass and can stop short of 76 kg (INVALID once in visit 3: 74.
- `CAULDRON_ACCEPTANCE_SCENES_ASSERT_CONTROL_RECOVER` — Implement Cauldron acceptance entry points, causal controls and recovery
- `CAULDRON_METAL_PERSIST_MEDICAL_PURGE` — Make Cauldron metal load persist until normal advanced medical purge
- `CAULDRON_ACID_ENDURING_PART_INJURIES` — Establish and complete Cauldron acid disfigurement and sensory persistence
- `CAULDRON_FALTER_MATCH_RULED_HOUR` — Reconcile Cauldron falter with the ruled one-hour warning
- `CAULDRON_FULL_SEAL_AMBIENT_PROTECTION` — Make full Cauldron sealing protect the worker on both ambient routes
- `CAULDRON_SITE_POOL_IDENTITY_THROUGH_USE` — Measure Cauldron site pool chemistry and preserve it through transfer
- `CAULDRON_GAS_RELOAD_AND_SEALED_BOUNDARIES` — Preserve active Cauldron combustion on reload and contain sealed boundaries
- `RIMMANDRAKE_RECONCILE_FLAGSHIP_CONTRACT_WITH_DELEGATED_PICK` — Reconcile flagship contract with the recorded delegated pick
- `RIMMANDRAKE_READ_WALK_TICK_COST_RUNNING_PAUSED_READ_ZERO` — ExplosiveKnockback walk: CARRIER_TICK_COST scored PASS on 0.0/0.0 ms in all 9 runs on record; jawa/time_perf reads 0 on a paused clock
- `RIMMANDRAKE_RESERVE_PUBLISH_BEAT_STARVED_THIRD_STUCK_ALARM` — Dispatcher publish starved by the beat budget trips publish:stuck: 3 alarms (11-15 14:58Z, 11-16 04:36Z, 11:40Z), each a 30+ min gap where the publish
- `GELATINOUSSLIME_ACCEPTANCE_SCENES_ASSERT_CONTROL_RECOVER` — Implement GelatinousSlime normal-action scenes, controls and exact recovery
- `GELATINOUSSLIME_ARCHIVE_LAST_TOUCH_AND_SINGLE_RETURN` — Reconcile last-touch archive fidelity, paid growth and single-return family state
- `GELATINOUSSLIME_SETTINGS_ACTIVE_CONSUMERS_AND_LEGACY_CONTACT` — Make active slime settings and scoped legacy contact match their authored promises
- `GELATINOUSSLIME_RAIN_COLLECTION_AND_DRAINAGE_RECONCILE` — Trace and reconcile the authored slime-rain water collection and drainage services
- `GELATINOUSSLIME_KIT_CHECK_NUMBERED_ANIMATION_FRAMES` — Resolve numbered Dwommo animation frames in the kit-art checker
- `RIMMANDRAKE_TRACE_SLACK_STAGE_SIX_SPEND_BEFORE_FIRST_VISIT` — Gimme Some Slack read USD 72.89 spent at Stage 6 (in-game) at 4:13 AM PST 2026-11-16 before in-game visit 1 of this arrival ran, so the 100 ceiling pa
- `RIMMANDRAKE_REBUILD_DISPATCH_VIEWS_ON_EACH_LAND_RETRY` — Dispatch land_ledger: a peer shard landing between origin_views' fetch and land.sh's push still leaves views stale (land.sh retries with the same view
- `RIMMANDRAKE_TRACE_DESIGNER_JUDGE_BLIND_TO_FILES_ON_DISK` — Designer stage judge read six slime files as missing while they sat in the Designer's clone
- `RIMMANDRAKE_KEEP_BRIDGE_HEARTBEAT_TO_HOLDER_CLONE_ONLY` — Any BENCH ledger event from any clone refreshes the shared bridge lock and stamps the writer's clone on it (cli.py:363 -> model.touch_shared_bridge; m
- `RIMMANDRAKE_ISOLATE_GAME_FREEZES_SMALLEST_LIST_BEYOND_ONE_MOD` — The game freezes for 50-100 ms at moments that do not depend on the mod under test (Explosive Knockback walk runs 4-7: most freezes land at the same m
- `RIMMANDRAKE_CARRY_GSS_GATE_ROWS_SCENES_NEVER_SAW` — validation.py --scenes-from reads only live rows; 6 GSS scenes want offline gate rows (O1..O8) that proof_all keeps only as a not_pass list, so they r
- `RIMMANDRAKE_FIX_GSS_BOX_ARMS_OFF_SLOPE_IN_CROWDS` — GSS: in crowded random layouts, cords leave junction-box arms off the stub's line/slope (device-stub boxes 16-57 deg, a box beside its own machine 38-
- `RIMMANDRAKE_DECIDE_GSS_HANGING_SWAY_LOST_ITS_ONLY_CORD` — GSS: the 'Hanging cords sway' setting and swayMode have no subject since the wall terminal's hanging wire was removed (owner 2026-11-16); retire them 
- `RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK` — Gimme Some Slack: bind the position-and-slope rule as a requirement (bar) of the mod with an offline sweep and a live bridge check: every art piece wi
- `RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT` — Gimme Some Slack: wind sway is for power-pole wires only. Remove wind sway from conduit-based wiring and wall tails (code, three settings, tests), and
- `RIMMANDRAKE_ROUTE_MODLEDGER_OWNER_GATES_VIA_CONDUCTOR` — selftest_conductor_authority red: modledger.py:2034 and modledger_backfill.py:296 owner gates lack the Conductor route
- `RIMMANDRAKE_RELEASE_CONTAGION_JUDGE_ONE_LOOK_HIS_WORD_GIVEN` — When the Contagion re-scope builder notes READY FOR ONE MORE LOOK: run coverage_judge.py release design/concepts/Contagion --why with his words 'Yes, 
- `RIMMANDRAKE_ISOLATE_RELENTLESS_GAME_SELFTEST_READS_OWN_CLONE` — selftest_relentless_game.py (t_blind_stall_probe_ends_attempt and the module run) CRASHES in any clone holding unlanded commits: relentless.finish cal
- `RIMMANDRAKE_PROVE_CONTAGION_GROWN_LIMBS_NEXT_VERSION_SWITCH_OFF` — Contagion Design Version 0.2.0 (Divergent): the Grown Limbs, all of it (five limbs, recipes, removal, Monstrous gestation, Monstrous-first injection);
- `RIMMANDRAKE_PROVE_CONTAGION_HELIX_TRADE_NEXT_VERSION_PRINTS_WAIT` — Contagion Design Version 0.2.0 (Divergent): Helix trade (draftprints, Helix contracts, curator caravan); deferred out of 0.1.0 by the owner 2026-11-16
- `RIMMANDRAKE_PROVE_CONTAGION_COALESCENCE_NEXT_VERSION_GAPS_KEPT` — Contagion Design Version 0.2.0 (Divergent): the Coalescence, all of it (formation, growth, cap, waiting pressure, Burn payoff, contact exposure); move
- `RIMMANDRAKE_BUILD_CONTAGION_DEFERRED_SWITCHES_OFF_SUITE_OPTS_IN` — Contagion 0.1.0 ships the Coalescence, Grown Limbs and draftprints/Helix switches OFF (moved to 0.2.0 by the owner 2026-11-16); the old live suite opt
- `RIMMANDRAKE_HARVEST_OWNER_WORDS_OFF_CONCEPT_ITEM_FOURTH_ASK` — Designer harvest: owner words recorded on a mod's other items never reach its concept (owner_uncited reads only the concept item)
- `RIMMANDRAKE_STOP_STEVE_GAME_FORCE_KILL_LEFT_IT_RUNNING` — SteveDesktop rw_game.sh down: force stop left the game running; taskkill /F by hand then killed it
- `RIMMANDRAKE_FIX_CONCEPT_TREE_SELFTEST_DESIGNER_ROW_DRIFTED` — selftest_concept_tree.py FAIL 1 on origin/main (seen 2026-11-16): 'Designer row exists, off, no slots' (line 758) expects the CONCEPT_AGENT_DESIGN_ARG
- `RIMMANDRAKE_REDECIDE_REPEAT_FINDINGS_JUDGE_COUNTED_AGAIN_TWICE` — Findings judge counts failed-again repeats (again=5) but never re-decides them, so they keep no outcome and flow.untriaged_findings sits at 5. Fix: pr
- `RIMMANDRAKE_TRACE_CONDUCTOR_SPEND_OVER_CAP_BY_EIGHT_AM` — Find what spent the Conductor's 1.07M weighted tokens before its 08:00 PST quick check on 2026-11-16 (advisory day cap 1.35M) and cut its cost without
- `RIMMANDRAKE_UNPIN_CRESTFEATHER_CHANCE_THE_TEST_HARDCODES` — Pyrelands: the crestfeather test pins the trophy chance at 0.35; read it from the mod instead
- `RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES` — Dispatcher role launches (9 of 9 rows) and rm-artpiped run in the Conductor's seat clone: give each its own clone and publish from it
- `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_TIER_EDGE_LANE_ONE_ONLY` — Polish: T_SHEET does not pin the 3 cm sheet-tier boundary
- `RIMMANDRAKE_PIN_FLOWWORKS_SPRINKLER_RADIUS_DEFAULT_UNWATCHED` — Polish: no test pins the sprinkler radius default or its 25-square label
- `RIMMANDRAKE_PIN_FLOWWORKS_TOSS_RANGE_AND_RELIGHT_UNWATCHED` — Polish: toss-flame range (provisional 4.9) and no-relight are unpinned
- `RIMMANDRAKE_PIN_FLOWWORKS_FETCH_FIRE_WINDOW_AND_KEY_UNWATCHED` — Polish: fetch-fallen under-fire window, warning key and interruptible flag unpinned
- `RIMMANDRAKE_PRUNE_ORPHAN_BUNDLES_FULLY_LANDED` — Orphan bundle store never pruned (359, 7.9 GB): judge by content against origin, delete the landed ones hourly
- `RIMMANDRAKE_REREAD_SCRUB_PINS_AFTER_PYRELANDS_GIANTS_MOVED` — LeaningScrub: re-read RM_PyrelandsGiants.cs and re-pin wildlife-zero-paths Z5 (Stage 3)
- `RIMMANDRAKE_MEND_COVERAGE_RECORD_SELFTEST_RED_SINCE_BAR_RULE` — selftest_coverage_refusal_record red on origin/main (re-ask case: contract None)
- `RIMMANDRAKE_STRIP_SCRUB_TEXT_WARDENS_CUT_BUT_STILL_SLEEPING` — LeaningScrub About.xml and felt description still promise the cut bark-wardens
- `RIMMANDRAKE_LAND_DESIGNER_RUN_DONE_BUT_NEVER_HARVESTED` — A finished Designer run the Dispatcher never marked done never landed its state; the orphan sweep should land it
- `RIMMANDRAKE_SKIP_CHAIN_CAPPED_CONCEPTS_IN_DESIGNER_STALL` — queues.designer.stalled_min counts concepts held by the Designer daily chain cap as stalled; exclude them like rejection_parked
- `RIMMANDRAKE_NOTE_FLOWWORKS_DRILL_DRAWS_POWER_WHEN_OFF_UNPINNED` — FlowWorks (Polish, Stage 6 inv_settings): no offline test catches a liquid drill drawing power while switched off or off in Mod Settings (blind cycle 
- `RIMMANDRAKE_NOTE_FLOWWORKS_COATING_LAWS_MISS_COLONISTS` — FlowWorks (Polish, Stage 6 inv_liquid_coating): the coating source laws stay green when colonists are never coated or a dug canal's liquid never coats
- `RIMMANDRAKE_NOTE_FLOWWORKS_SHEET_TOOLTIP_TWO_CM` — FlowWorks (Polish): the crops-drown tooltip says 'at least 2 cm' while the kernel's standing tier starts at 3 cm rising (2 cm falling)
- `RIMMANDRAKE_FIX_KNOCKBACK_RAID_NULL_PAWN_STORM_780_TICKS` — ExplosiveKnockback raid walk throws two NRE storms: 780x 'Exception ticking Levin' in vanilla Pawn.Tick+0x60 at (246,0,36) and 447x root Update NRE in
- `RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS` — Keep the Maturation Pipeline's stage ceiling and run caps in weighted tokens, not list dollars: maturation_dispatch.json cap_usd, stage_ceiling_usd, b
- `RIMMANDRAKE_PIN_PYRE_ORDINARY_RAIN_LIST_RIGHT_BUT_UNTESTED` — Pin Pyrelands' ordinary-rain list with an offline test
- `RIMMANDRAKE_POLISH_PYRE_PROBE_EXPECTED_SKIPS_POLLUTION_CLAMP` — Ash probe's expected skips the polluted-cell clamp
- `RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_SIX_RULES_LANE_ONE_CAUGHT` — Graffiti T_FUZZ misses six kernel rules the blind lane 1 catches (budget cap, visit cap, numb good, craft Normal, scrawl ceiling, fight from nothing).
- `RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS` — Graffiti bar ugliness_visible pins def Beauty -15/-3, but a painted mark's inspected beauty is craft-only (equal for same-hand scrawl and tally at Awf
- `RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD` — Maturation Stage 3 exit passed Graffiti with locked bar raider_pressure wholly unbuilt; record.json impl is frozen at lock, so no live signal exists t
- `RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS` — Maturation tick: a designer_blocked pause whose reason names a ledger item that is already done must re-read its gate and either lift or name what is 
- `RIMMANDRAKE_BATCH_DETACHED_ITEM_STATES_SEVENTY_EIGHT_REPLAYS` — rm-running times out every minute: fleet_mods.detached_done ran one rimflow show per finished helper (78 x 1.8 s = 140 s > 90 s)
- `RIMMANDRAKE_FINISH_SLACK_TONIGHT_TWO_DECIDERS_RED_AT_CERTIFICATE` — Gimme Some Slack: turn its two red offline deciders green (T_CORD_GEOMETRY_OFFLINE, T_STUB_JOINS; live check read 393 cords on 394 stubs, 23 off-slope
- `RIMMANDRAKE_TOUGHEN_DESIGNER_ENTRY_GATE_VAGUE_BUILDS_CHOKED` — Design, with him, a harder definition gate between the Designer and the build step (precision and completeness of every bar before a mod may enter the
- `RIMMANDRAKE_RETIRE_FRIVOLOUS_BIOME_CONTENT_TESTING_PRICE_KNOWN` — Per held biome mod, list its content and bars with what each costs to test, and bring him a cut list to rule on. Acceptance test: none, an owner decis
- `RIMMANDRAKE_UNJAM_DISPATCH_CLONE_UNTRACKED_TWIN_FROZE_IT` — The dispatch clone (~/rm/dispatch) sat ahead 47 / behind 21 from 3:10 to 5:46 PM PST 2026-11-16: an UNTRACKED conversations/2026-11-16-2236-1d9fed6f.m
- `RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN` — Gimme Some Slack live-end geometry: sweep the whole space in Python, and where a bare cord cannot hold the bars, invent, unify or propose a relaxation
- `RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY` — Write the ruling into standing_rulings.md and build it into the Maturation Pipeline: a builder that oscillates between conflicting bars must prove the
- `RIMMANDRAKE_REPAIR_BAR_RULE_SELFTEST_RED_BLOCKS_PUBLISH` — selftest_bar_rule_tuning_numbers is red on origin/main (case 5: a new gap on unchanged material at a later look reads not_covered, not advisory) and r
- `RIMMANDRAKE_UNSTICK_PULSE_DEPLOY_GIT_SIXTEEN_TIMEOUTS_A_DAY` — rm-deploy-update: git pull in the pulse-deploy checkout on D: times out (16 skips in 24 h, measured 19:18 PST 11-16); twice it went over an hour with 
- `RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH` — Scratch cleaner archives tiny test clones slower than they are made
- `RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE` — Pyrelands: Fable Rescue on the fire-against-black-rain conflict and its unspecified mechanics (brief roles/fable_rescue.md). Acceptance test: the resc
- `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS` — The Dispatch tick left ExplosiveKnockback (blind cycle 5) and Pyrelands (blind cycle 3) waiting over six hours with the game free: find why, fix it, a

## Commits

```
7c57676a95 ledger: owner answers (as-built whip, GSS top priority), ExplosiveKnockback ceiling release
9b53f8d1b7 seat_dirt: land 3 safe path(s) left in the seat clone (conversation records, filed item prose)
249d1ee36f selftest_bar_rule: the later-look case stubs the brief CALIBRATED instead of reading the live registry The live coverage_judge brief reads UNTESTED since its last edit, which made the case's first refusal advisory and its second look full.
730f011ecb Graffiti: a same-hand scrawl inspects uglier than a tally at every craft (MarkBeauty, ScrawlVandalism) Owner card 2026-11-16 'Look and stat agree' (OWNER:1794889675303725702). T_UGLINESS_OFFLINE red on the base at awful and poor; live sc_beauty_pair reads RM_GraffitiStage.Pair. bar_rule.detect now flags a stat named with its number ('Beauty -15', 'stats read -15').
1b699914ff maturation: spend rows of ended runs (Dispatch step)
5ad6cf1f10 modledger: judge run judge-1794890427 on ExplosiveKnockback started (Dispatch step)
60e7bf6a12 ledger: maturation dispatch filed RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FIVE
20f65d718e ledger: RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS clone bundled
adda72b075 ledger: RUNNER ingest of 0 testq job(s)
cbec0d571e conversations: catch-up 1 record(s)
90224be7e3 ledger: detached run on RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS ended
c536762c38 ledger: RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS note; lesson: a standing alarm hides a new pause
356a61c064 Pyrelands: Conductor hold on stage 4+5 while the Fable rescue run reworks fire and rain
6f3ca6369f maturation next reads the Dispatch tick's own decision: a ceiling pause no longer prints "automatic"
ab69dab291 ledger: RUNNER ingest of 0 testq job(s)
04998ccc15 ledger: RUNNER ingest of 0 testq job(s)
5d46371014 ledger: owner card on Graffiti ugliness_visible wording
c0ddd8e3d7 ledger: RUNNER ingest of 0 testq job(s)
42483a7578 ledger: RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE note
1b032c6add ledger: RUNNER ingest of 0 testq job(s)
... 1534 more: git log --oneline 526a107407..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-16T17:32:29Z

Working tree clean apart from untracked `Transient/`.

