# Old-era ticket sweep, 2026-11-18

Item `RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD`, a detached run, 2:45 PM PST onward. The Conductor, on the owner's words of 2026-11-18 about 2:10 PM PST: *"Of those old-era tickets, any of them not worked but found still valid should be worked and closed at this time. No more stale pipeline crud."*

## How the tickets were found

- `model.replay()` over the whole ledger [measured]: 8,841 items, 2,130 open (proposed, ready, doing, built, validated), **1,647 open and filed before 2026-11-13**.
- System subject, by id prefix (the second word after `RIMMANDRAKE_`/`RIMMASTER_`) and then by reading every candidate's title: 499 candidates, plus 14 machinery tickets the 2026-11-15 sleeper census listed under content-looking prefixes; 139 mod, art, world or design tickets removed by hand. **377 in scope** plus the one added by name, 2 of them later found to be mod content (`OUT`), so **376** worked here.
- Probe that the query sees known old tickets: all eight tickets the brief names are in the set (`BLINDCHECK_PROVE_VERDICTS_EATEN_BY_DISK`, `LIVEPROOF_REDEPLOY_FIX_TRIPS_PEER_DLL`, `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE` and the five 2026-11-01 RECONCILE builds). The brief's two parked tickets (commit 550bf70d9f, CONDUCTOR notes 21:25Z) are `ROLE_HEADERS_RETIRE_ENABLED_PROSE` (in the set) and `RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES` (an art-sheet tool ticket the title read had put under art; added back by name) [measured].
- Not in scope: concept anchors (`design/concepts/<Mod>/stage.json` items), mod content, art, biome, world and design tickets. 323 of the 375 have no prose file: their title is their whole spec.

## How each verdict was reached

- **DONE**: a commit naming the item landed on origin/main and every selftest those commits touched exits 0 on HEAD in this run (204 selftests run, 8 at a time, 170 s cap each) [measured]. Whether every clause of an old title is met was not re-read clause by clause [guess ~85%]. Closed with `rimflow close --sha <that commit>`.
- **CLEARED**: the thing it reported is no longer happening: its alarm is not open in `ops_watch/alarms.json` (read 2026-11-18 22:52Z), its timer is active, or its red selftest is green now. Dropped with `stale-drop: <the probe>` (CHARTER stale default).
- **DEAD**: its target was retired or removed (Relentless 2026-11-13; the arena 1f0e666566; RimPulse 2026-11-03; the Arbiter; the disabled Producer and Auditor roles), or it was parked by the owner's 2026-10-29 card as old workflow and names no failing behaviour. Dropped with the reason.
- **DUPLICATE**: superseded into the named survivor.
- **VALID SMALL**: built here, test first.
- **VALID LARGE**: still true and more than about an hour, or needs a machine this run may not touch (SteveDesktop, the game). Left open with a note saying what it needs.
- **LIVE ONLY**: built work whose remaining criteria are live game runs; the game is off-limits to this run. Left open.
- **KEEP**: a live alarm's current item or a standing host something still files onto. Left open.
- **DONE, GUARD OWED**: DONE by the same test, but the item was closed once before and its live promise broke since (deadman), so `rimflow close` refuses it until a class guard test is shown failing on the instance (`rimflow guard`) or the Conductor lifts the guard. Left open with a note; the deaths were mostly aggregate alarms read as each fix's relapse, the 2026-11-07 timer stop, and 2026-11-08 hook-wiring reads from a clone without hooks [measured: deadman `live broken` events].
- **NEEDS HIM**: one question each.

## Counts

| verdict | count |
|---|---|
| DONE | 29 |
| DONE_GUARD_OWED | 69 |
| CLEARED | 30 |
| DEAD | 73 |
| DUPLICATE | 6 |
| VALID_SMALL | 1 |
| VALID_LARGE | 121 |
| LIVE_ONLY | 38 |
| KEEP | 7 |
| NEEDS_HIM | 2 |
| OUT | 2 |
| total | 378 |

## DONE (29)

| ticket | state at census | evidence |
|---|---|---|
| `ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING` | ready | switching_plan.py runs from account-plan.timer (active); the skill shipped at c1651115d3; selftests green |
| `AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO` | ready | work landed c5c07b9e25; its 3 selftest(s) exit 0 on HEAD in this run |
| `ALARM_FILING_FIX_NO_ROOM_AT_INN` | ready | work landed ba566f60c7; its 1 selftest(s) exit 0 on HEAD in this run |
| `CHECKER_REACH_FIX_GH_DARK_SECOND` | ready | work landed c549cc8ab6; its 1 selftest(s) exit 0 on HEAD in this run |
| `CLEANER_SANITY_REVIEW_FINISH_FULL_FILES` | ready | work landed 3bf4cecd5f; its 4 selftest(s) exit 0 on HEAD in this run |
| `CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY` | ready | work landed c043da2443; its 1 selftest(s) exit 0 on HEAD in this run |
| `CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES` | ready | work landed b47c87d04b; its 1 selftest(s) exit 0 on HEAD in this run |
| `DELEGATED_DIGEST_HARDEN_MUTATION_SURVIVORS` | proposed | the red-first mutation-kill selftest it asked for landed at 68b347c069; selftest_delegated_digest green |
| `DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH` | ready | deploy_def_guard.DEPLOY_EXCLUDE_DIRS now includes art_candidates (line 73); selftests green; work landed f160d57cf8 |
| `DRVFS_ENOMEM_FIX_ORDER_SEVEN_RUNS_DRY` | ready | work landed 34283c8415; its 1 selftest(s) exit 0 on HEAD in this run |
| `EVIDENCE_HEAD_SEAL_REPAIR_THREE_BEHIND` | ready | work landed 9df1e805ad; its 1 selftest(s) exit 0 on HEAD in this run |
| `LESSONS_RETIRE_INBOX_AS_QUEUE` | ready | work landed 47595a6360; its 1 selftest(s) exit 0 on HEAD in this run |
| `LOG_BOUND_DECIDE_COLD_LOAD_ALWAYS_GUILTY` | ready | work landed 9d974a4e3c; its 1 selftest(s) exit 0 on HEAD in this run |
| `MIRROR_PACK_REPAIR_STILL_GRUMBLING` | ready | work landed 1a553c5002; its 2 selftest(s) exit 0 on HEAD in this run |
| `OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT` | ready | work landed ee749bf033; its 2 selftest(s) exit 0 on HEAD in this run |
| `OPS_ERROR_BUDGET_DIAGNOSE_CIRG` | ready | work landed 22f53ea356; its 2 selftest(s) exit 0 on HEAD in this run |
| `OPS_METRONOME_MIGRATE_CLOCKS_FENCED` | ready | work landed aa928335da; its 11 selftest(s) exit 0 on HEAD in this run |
| `OWNER_ASKS_AUDIT_FIFTY_NINE_DEEP` | ready | work landed f03c025e7e; its 1 selftest(s) exit 0 on HEAD in this run |
| `PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS` | ready | 18178d9350; its cases (1, 1b, 1c) pass in selftest_prooflint_at_filing.py on HEAD |
| `PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN` | ready | file, implemented and close all call the lint (cli.py 2038, 2855, 3082); the only red, selftest check 7, counted call text and missed the preflight-gate route since 31c94dd37a: fixed at e6ab733c03, a mutant with the close call removed is caught |
| `REGRADE_SAMPLE_BUILD_NOISE_GUARDED` | ready | work landed df7cadb8b9; its 1 selftest(s) exit 0 on HEAD in this run |
| `REPO_RENAME_SYMLINK_RETIRE_1` | ready | D:\Luke\dev\Rimworld no longer exists; the last old-path reference was repointed at e148e8c31e; the remaining mentions are hook guards on purpose |
| `RESTOREWAIVER_AUDIT_TEN_TAKEN_ON_TRUST` | proposed | 746fd15844: selftest proves each waived restore; green on HEAD |
| `ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS` | proposed | the red-first golden mutation-kill selftest it asked for landed at 6dcfd7f682; its selftests green |
| `SEAT_TMP_PRUNE_TESTS_LEFT_LUGGAGE` | ready | work landed e9221a885c; its 1 selftest(s) exit 0 on HEAD in this run |
| `SLOT_HOOK_FIX_TEXT_STILL_OWNER_ONLY` | proposed | 0535dcc043 (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM) rewrote every his-words gate; the hook's selftests green |
| `STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE` | ready | work landed 5f7d5b0d57; its 5 selftest(s) exit 0 on HEAD in this run |
| `TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD` | ready | work landed 6607725538; its 4 selftest(s) exit 0 on HEAD in this run |
| `TMP_SCRATCH_PRUNE_SIXTEEN_GIGS_NOBODY_CLAIMS` | ready | work landed 7385b7d55d; its 1 selftest(s) exit 0 on HEAD in this run |

## DONE_GUARD_OWED (69)

| ticket | state at census | evidence |
|---|---|---|
| `ACCOUNTPLAN_FIX_UNDOES_SWITCH_IN_FOUR_MIN` | ready | work landed fe7ed5afda; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `AGENT_IMPROVE_INSTALL_DAILY_TIMER` | ready | rm-agent-improve.timer enabled and active now; unit landed in 6ee19ad490; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `AGENT_IMPROVE_REPAIR_SILENT_NONE` | ready | work landed 6ee19ad490; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED` | ready | work landed 3e0b001eb4; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `ALARM_RANGES_BUILD_CLASSES_AS_DATA` | ready | work landed 570e4d3b27; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `ALARM_REPEAT_FIX_BREAK_ON_WORSE` | ready | work landed 547224ce01; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR` | ready | block_blanket_git_stage.py refuses a bare 'git commit --amend' (its docstring line 27; selftest green); work landed 1023093a75; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `ARTPIPE_ORPHAN_UNSTICK_WEDGE` | ready | work landed 9b5e7b04d2; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `CALL_DEADLINES_ENFORCE_130_OPEN_ENDED` | ready | work landed 7a9249afe8; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `CHECKER_DEATHS_ALARM_BUILD_29_WENT_UNHEARD` | ready | work landed 44daff0c93; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `CHURN_WATCH_BUILD_NAMES_EVERY_BOUNCER` | ready | work landed f0403eeadd; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `CONDUCTOR_CLOSEOUT_BUILD_LEDGER_CHECK` | ready | work landed b00bfae65c; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `CONDUCTOR_REBOOT_FIX_THREE_WASTED_MINUTES` | ready | b483dac198: the Conductor handoff reboots via --now; selftests green; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `DELEGATED_CARDS_FIX_HELD_OUT_RECALL` | ready | selftest_block_delegated_cards.py exits 0 on HEAD; the bar was settled at 2315f1b614; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `DESIGNER_ANSWERED_MONITOR_WAITING_ON_NOBODY` | ready | work landed f6b6c6dad9; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `DESIGNER_STALL_MONITOR_READY_AND_FORGOTTEN` | ready | work landed 3ccda6ef54; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `DISK_WATCH_BUILD_SCRATCH_OUTSIDE_CAP` | ready | work landed bb1fdf8e7d; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `EXPEDITE_LANE_BUILD_JUMPS_THE_GAME_QUEUE` | ready | work landed fdf1374675; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HANDOFF_FIX_RESTART_TWENTY_SECONDS` | ready | work landed ae07aa74b1; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HANDOFF_HOOK_FIX_QUOTED_READY_COUNTS` | ready | work landed e7d62cabf4; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HANDOFF_RESTART_AUDIT_FILES_OWED` | ready | work landed 53b8748973; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HELPER_REGISTRY_BUILD_DURABLE_RECEIPTS` | ready | work landed e8b334a354; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HOOKS_BLINDSCAN_TUNE_DRIVE_D_IMPORT_TOLL` | ready | work landed 355bdc8b71; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST` | ready | work landed a2bac49a9a; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS` | ready | work landed 2160831515; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `IDLE_SEAT_RESTART_BUILD_BRINGS_QUIET_BACK` | ready | work landed faaab9f5fe; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `IDLE_WATCH_BUILD_SEAT_MINUTES_IN_DIGEST` | ready | work landed 480705561c; its 3 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `INCIDENT_LEDGER_BUILD_TOLD_ACKED_RECOVERED` | ready | work landed c09e663226; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `ISSYSTEM_WORDS_FIX_PIPELINE_READ_AS_CONTENT` | ready | work landed a5cba06368; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `LENT_ALARM_MEASURE_THE_LOAN_NOT_WEEK` | ready | work landed 36b504cba2; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `MODCHECK_VALIDATE_BUILD_DELEGATED_NEW_BARS` | ready | work landed 13e4c16f45; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `NIGHTLY_REDS_FIX_RERUN_BEFORE_PAYING` | ready | work landed f1574ed294; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPERATIONS_FIX_RUNS_BLIND_WHEN_STALE` | ready | work landed 21dd9677e9; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_ALARMS_FIX_FIXED_ITEM_ID` | ready | ops_watch.mint_name keeps one fixed id per alarm (4f64d24ce3); alarms.json reuses OPS_PLAN_LIST_FIX_VMIV across refilings; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY` | ready | work landed 0f3e9fcd6f; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV` | ready | work landed 42647172c7; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 6 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_FINDINGS_DIAGNOSE_17B4` | ready | work landed fb038d5c4c; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_FINDINGS_DIAGNOSE_XZLM` | ready | work landed 65a1f109c7; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 14 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_GAME_HEALTH_DEBUG_PXQI` | ready | work landed b397bc0152; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 21 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_HEALTH_FIX_BROKEN_RULES_READ_HEALTHY` | ready | work landed d61e43685d; its 4 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_HEALTH_RANK_FIX_GLOB_OUTVOTES_EXACT` | ready | work landed 5d4d5ea0a6; its 4 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_HEALTH_WIRE_INSTRUMENT_INCIDENTS` | ready | work landed 552f9d8bd4; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_JUDGE_NOTES_MEASURE_VS_NO_CHANGE` | ready | work landed 0166bd1228; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_MEMORY_VET_THEN_WIRE_AFTER_WATCH` | ready | work landed ac39eccf39; its 5 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_QUEUES_READING_RESTORE_HQXV` | ready | work landed a04f9d6f7a; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_RAISE_REWIRE_WITH_DEATH_LADDER` | ready | work landed 7d9928c0d0; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_REFUSAL_REWIRE_TO_CONDUCTOR` | ready | work landed b105e9a9c9; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_ROLE_DIAGNOSE_STARVED_AT_FOUR_RUNS` | ready | work landed 307feed8ee; its 4 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_STEVE_UNSTICK_UNCLAIMED_ETBS` | ready | work landed e70d1b821a; its 3 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 13 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_STEVE_UNSTICK_VHRP` | ready | work landed 87551b29f0; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `OPS_TESTQ_UNSTICK_ECPK` | ready | work landed 0400ec93c9; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT` | ready | work landed 9a8c54a9f7; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 3 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN` | ready | work landed de44537a98; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `PULSE_DEPLOY_UNSTICK_DIRTY_CHECKOUT` | ready | work landed 2fc8d23cf9; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `QUEUE_STALL_ALARM_FINISH_THE_STRAGGLERS` | ready | work landed 80d3d18393; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `RED_COP_BUILD_NO_ORPHAN_REDS` | ready | work landed f0492bc10c; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `RELAPSE_OPS_WATCH_FIX_DIED_TWICE` | ready | work landed 6997fe8331; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `RELAPSE_QUEUES_FIX_DIED_TWICE` | ready | work landed ff9168747b; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `RELAPSE_TIMERS_FIX_DIED_TWICE` | ready | work landed b59fb5b7f1; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN` | ready | b0fb6fe124: a fix that died closes only with a guard; its tests green except selftest_relentless.py, red on HEAD for the retired pool (retired-eras index); it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `RESTART_JOIN_BUILD_EVERY_GOODBYE_ENDS` | ready | work landed 307c7f3ac5; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `ROLE_USE_MEASURE_OUTPUT_READ_AND_ACTED` | ready | work landed ac1d9e74eb; its 4 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `SCRATCH_STRANDED_FIX_SHARDS_CRY_WOLF` | ready | work landed 041f74af4c; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS` | ready | work landed 48c6bd7ab1; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 2 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `SPAWN_HOOK_FIX_TYPING_BEATS_OWNER_CAP` | ready | work landed dd677f6ecf; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `STATION_NOTEBOX_BUILD_WHISPER_AT_NEXT_TURN` | ready | work landed 8be5e40536; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `STEWARD_FIX_ENDS_ON_GREEN_NOT_RUNNING` | ready | work landed 9020b92322; its 1 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `STEWARD_FIX_LEAVES_THE_LIGHTS_ON` | ready | 5bd612281f: steward retires what a recovered incident left; selftests green; it was closed before and its live promise broke 1 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |
| `WORKER_CLONES_MONITOR_POOL_NOT_RABBITS` | ready | work landed 5e603a1d82; its 2 selftest(s) exit 0 on HEAD in this run; it was closed before and its live promise broke 3 time(s) (deadman), so rimflow refuses the close until a class guard test is shown failing on the instance (`rimflow guard`), or the Conductor lifts it |

## CLEARED (30)

| ticket | state at census | evidence |
|---|---|---|
| `CLASS_REFS_FIX_UNRESOLVED_PIPESYSTEM` | proposed | selftest_lint_def_type_refs.py and selftest_paint_list.py exit 0 on HEAD in this run |
| `DEPLOY_UPDATE_UNSTICK_ART_EVENTS_BLOCK_PULL` | ready | no DEPLOY_STALE alarm open in ops_watch/alarms.json at 2026-11-18 22:52Z |
| `HELPER_RECEIPTS_FIX_KILL_READS_CRASH` | ready | selftest_helper_receipts.py exits 0 on HEAD in this run |
| `L1DONOROFF_FIX_SARLACC_LEFT_THE_PIT` | proposed | selftest_l1_donor_off_round.py exits 0 on HEAD in this run |
| `L1_DONOR_SELFTEST_FIX_READS_A_GHOST` | proposed | selftest_l1_donor_off_round.py exits 0 on HEAD in this run |
| `L1_DONOR_SELFTEST_FIX_SARLACC_GONE_MISSING` | proposed | selftest_l1_donor_off_round.py exits 0 on HEAD in this run |
| `LIVE_RESTORE_DISPATCHER` | ready | the Dispatcher runs as the metronome's dispatch phase; ops_watch read 2026-11-18 22:52Z |
| `LIVE_RESTORE_OPS_WATCH` | ready | ops_watch alarms.json last_seen 2026-11-18T22:52Z, fresh |
| `LIVE_RESTORE_RM_ARTEVAL_AUTOJUDGE` | ready | rm-arteval-autojudge.timer active now; fix landed c36201df60 |
| `LIVE_RESTORE_RM_ARTPIPE_IDLE_FILL` | ready | rm-artpipe-idle-fill.timer active now (systemctl --user, 2026-11-18) |
| `LIVE_RESTORE_RM_MEMWATCH` | ready | rm-memwatch.timer active now; deadman last read it kept |
| `LIVE_RESTORE_RM_MIRROR` | ready | rm-mirror.timer active now |
| `LIVE_RESTORE_RM_OBJSTORE` | ready | rm-objstore.timer active now |
| `NOW_FLAG_FIX_NAMED_TWICE_OOPS` | proposed | selftest_restart_now.py exits 0 on HEAD in this run |
| `ONE_PATH_SEAM_FIX_LOCALSLOW_LITERAL` | proposed | selftest_one_path_seam.py exits 0 on HEAD in this run |
| `OPS_ARTPIPE_UNSTICK_RBLV` | ready | no QUEUE_STALLED alarm open (alarms.json 22:52Z) |
| `OPS_DEADMAN_REVIVE_17EC` | ready | the Dispatcher runs in the metronome's dispatch phase; no dead-man alarm open |
| `OPS_DEPLOY_UPDATE_UNSTICK_RDHQ` | ready | no DEPLOY_STALE alarm open (alarms.json 22:52Z) |
| `OPS_DISK_DRAIN_XPPR` | ready | no DISK_LOW alarm open (alarms.json 22:52Z) |
| `OPS_RESTART_UNSTICK_BENCH_YCVY` | ready | a 2026-11-05 restart request; no restart alarm open now |
| `OPS_SCRATCH_OUTSIDE_CAP_DRAIN_CLCI` | ready | no SCRATCH_OUTSIDE_CAP alarm open (alarms.json 22:52Z) |
| `OPS_STEVE_SEATS_RESTORE_QTWK` | ready | no STEVE_SEATS alarm open (alarms.json 22:52Z) |
| `OPS_WORKER_CLONE_POOL_RESTORE_HMOQ` | ready | no CLONE_POOL_BREACH alarm open (alarms.json 22:52Z); work landed 9a54fab0cf |
| `REPLAY_BANK_STALE_BUILD_RED_AT_HEAD` | proposed | selftest_validator_mutants.py exits 0 on HEAD in this run |
| `RETIRED_UNITS_PRUNE_PULSE_STILL_TICKING` | proposed | no rm-pulse timer exists now (rm-pulse.service masked); the pulse-deploy checkout is kept on purpose (retired-eras index Phase 2) |
| `RIMMASTER_REPAIR_SEAT_FILE_CHECK_RED_BEFORE_THIS_TOO` | proposed | selftest_bridge_seat_relentless.py exits 0 on HEAD in this run |
| `ROLE_RUN_NOW_FIX_ELEVEN_SLOT_RED` | proposed | selftest_role_run_now.py exits 0 on HEAD in this run |
| `SBXD_FARMS_HUNT_MAKER_NOBODY_ADMITS` | proposed | no ~/.seat-tmp/BENCH/sbxd* remain (ls: 0); the maker was the seed-wall selftest litter, fixed at c0c11ac0e9 |
| `SELFTEST_DISPATCHER_FIX_NINE_RED_BEFORE_ME` | proposed | selftest_dispatcher.py exits 0 on HEAD in this run |
| `WTPROFILE_FIX_TESTS_STILL_ASK_FOUNDRY` | proposed | selftest_seat_restart.py exits 0 on HEAD in this run |

## DEAD (73)

| ticket | state at census | evidence |
|---|---|---|
| `ACCOUNTPICK_HOLD_RESTORE_WHEN_HE_LANDS` | proposed | his later ruling 2026-11-02 (TOKEN_LIMITS_TAME_BARK_NO_BITE) set account_pick hold to [] on purpose: dispatcher_schedule.json account_pick._hold_override |
| `ACCOUNT_MOVE_FIX_ADVICE_WITH_NO_HANDS` | proposed | switching_plan.py now switches accounts (account-plan.timer active); his 10-28 burn card was replaced by his 2026-11-17 orders in the live plan |
| `ACCOUNT_PICK_HARDEN_UNRESOLVED_CURRENT` | proposed | account_pick is advisory: act=recommend and hold=[] (owner 2026-11-02, dispatcher_schedule.json); its hold flag decides nothing |
| `ACCOUNT_SWITCH_FIX_HAND_STEP_BEFORE_MONDAY` | proposed | a one-off for 2026-11-02 04:00Z, passed; accounts are switched by switching_plan.py |
| `ALLOCATOR_ENFORCE_LENT_BURN_ACCOUNT` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); the lent account's line now lives in switching_plan (steven leave_pct_left), not the slot allocator |
| `ARENA_VERDICT_EXPLAIN_PROMISED_AT_GOODBYE` | proposed | the arena trial ended and its code was removed at 1f0e666566 (owner card 2026-11-05) |
| `AUDITOR_IMPORTS_VET_PIL_THEN_LXML_MISSING` | proposed | an Auditor rule candidate; the Auditor role is disabled (dispatcher_schedule.json roles: Auditor enabled false), so nothing would run it |
| `BLINDCHECK_PROVE_VERDICTS_EATEN_BY_DISK` | ready | re-runs Relentless blind checks; the blind judge retired with Relentless 2026-11-13; dropped with --release-dependents |
| `BOUNDED_TMPDIR_FIX_RUN_DIR_OVERWRITTEN` | proposed | 'unwalled workers' were Relentless's; claude_bounded.sh seat temp is the intended per-seat dir (line 62) |
| `BOXTOOLS_HARDEN_IMPORTS_PLANTED_CV2` | proposed | evidence.box_tools no longer exists in src (git grep finds no box_tools); it served Relentless's box checks |
| `BUNDLE_SHRINK_NOISE_DIFFS_NINE_GB` | proposed | relentless.py pool bundles were the tick's (Phase 2 of the retired-eras index: tick dead); the scratch archive backlog is today's RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH |
| `CLONEBYTES_REWIRE_OFF_TICK_NEW_THIRD` | proposed | the tick it would detach from is Relentless's (masked 2026-11-13) |
| `CLOSE_EVIDENCE_HARDEN_MUTATION_SURVIVORS` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); names a mutation score, no failing behaviour; re-file on a real escape |
| `CLOSE_EVIDENCE_WIRE_RUNNER_SEAT` | proposed | fed the Arbiter's G6 check; the Arbiter is retired (CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES, b47c87d04b) |
| `COMMIT_SESSION_FIX_NAMES_WINDOW_NOT_HELPER` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); the trailer fed the retired Arbiter's independence check |
| `COMPACTION_LOG_FIX_HELPERS_COUNTED_AS_SEAT` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a log reading of 2026-10-26, no consumer named |
| `COMPACTION_RESTORE_OPEN_ITEMS_FROM_LEDGER` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); CLAUDE.md Compact Instructions now require every open NEXT pointer with its id |
| `CONDUCTOR_BRIEFING_DESIGN_ONE_PAGE_NOT_SIX` | proposed | keyed to the RimPulse pages (retired 2026-11-03); MATURATION_NOW and STATUS_BOARD brief him now |
| `DEAD_FIXES_REPAIR_TEN_NOT_WORKING` | ready | the ten fixes are named in no prose or note; a 2026-10-31 sample since overtaken by the 2026-11-15 sleeper census and the 2026-11-18 triage |
| `DIGEST_LEFTOVERS_FIX_DROWNS_THE_READER` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a 2026-11-01 digest reading |
| `ESCAPE_RECORD_BUILD_PLAIN_TAGS` | proposed | records Relentless escapes; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `EVIDENCE_KEY_HARDEN_AGENTS_CANNOT_READ` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a same-user key cannot be hidden from same-user agents; the v3 evidence mac it guards fed the retired Arbiter |
| `GAMEENV_FIX_HARNESS_C5CF41AB_ITEMS_WAIT` | proposed | a Relentless game-lane environment cause; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `GAMEENV_FIX_PROOFSITE_102FDD57_ITEMS_WAIT` | proposed | a Relentless game-lane environment cause; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `GAMEENV_FIX_PROOFSITE_54339AD0_ITEMS_WAIT` | ready | a Relentless game-lane environment cause; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT` | ready | a Relentless game-lane environment cause; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `GAMEPHASE_UNBLOCK_HELD_GAME_SITS_IDLE` | proposed | Relentless game phases; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `HELPER_BUDGET_GATE_ENFORCE_NOT_ASKING_NICELY` | proposed | replaced by spend_watchdog.wrap (owner 2026-11-16: no launched agent is told its spend; a hard cap stops it from outside) |
| `HELPER_CAPTURE_HARDEN_FWALK_SWAP_PIN` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a mutation-score item, no failing behaviour |
| `HELPER_IDS_RESTORE_AFTER_COMPACTION` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); CLAUDE.md Compact Instructions item 5 now requires running subagents' name/ID |
| `HELPER_WAITS_FIX_CACHE_COLD_REWRITES` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); sessions now use a 1-hour prompt-cache TTL, so the 5-minute cold-cache rewrite it measured no longer applies |
| `HOLD_SELFTEST_FIX_RED_ONLY_WHEN_ISOLATED` | proposed | blocked Arbiter passes; the Arbiter is retired |
| `ISOLATED_EVIDENCE_HARDEN_MUTATION_SURVIVORS` | proposed | isolated_evidence.py no longer exists in the tree |
| `LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN` | proposed | already true: a claim now issues a per-attempt lease token (this run's claim printed --token BENCH.pid21523.f904ba73) |
| `LEDGER_MOD_FIELD_DECIDE_OR_DROP` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); the Maturation Pipeline keys work by mod through design/concepts/<Mod>/stage.json |
| `LESSONS_BACKLOG_DRAIN_SINCE_SEPTEMBER` | proposed | superseded by LESSONS_RETIRE_INBOX_AS_QUEUE (47595a6360): lessons are a corpus, not a queue |
| `LIVEPROOF_REDEPLOY_FIX_TRIPS_PEER_DLL` | proposed | the Relentless live proof is retired; today's live drivers set MODCHECK_SKIP_DEPLOY (16 Python references in src) |
| `LIVE_MODS_MEASURE_WEEK_AFTER_ROLL_CALL` | ready | measures Relentless runs.jsonl rows; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `LIVE_RESTORE_RM_DISPATCHER` | ready | rm-dispatcher.timer is disabled on purpose: the metronome's dispatch phase owns that clock (metronome_phases.json) |
| `LIVE_RESTORE_RM_OPS_WATCH` | ready | rm-ops-watch.timer is disabled on purpose: the metronome's sense phase owns it since 2026-11-05 (metronome_phases.json) |
| `LIVE_RESTORE_RM_RESTART_RECONCILE` | ready | rm-restart-reconcile.timer is disabled on purpose: the metronome's raise phase owns it since 2026-11-04 (metronome_phases.json) |
| `METRICS_FOLLOWUPS_FINISH_STILL_STRETCHING` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); includes a RimPulse row group (RimPulse retired) |
| `MODSFP_REWIRE_OFF_TICK_MISS_WALKS_INLINE` | proposed | the showing stage was a Relentless stage; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `MODS_ACCEPTED_DECIDE_ZERO_OF_THE_LOT` | proposed | the 'mods accepted' count was on the Relentless progress page; mod status is maturation_dispatch.py status now |
| `MOD_COMPLETION_MEASURE_HOW_DONE_IS_DONE` | proposed | superseded by the Maturation Pipeline's per-mod stages and Design Versions |
| `NEEDS_YOU_DRAIN_NINE_ALREADY_ANSWERED` | proposed | the nine are unnamed; the 2026-11-15 sleeper census redid this read (15 answered items, moved) |
| `PARALLEL_BUILD_REVIEW_DEFEND_EVERY_LIMIT` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); the limits it reviewed were replaced (16-clone pool approved by the owner) |
| `PIPELINE_RETHINK_OWNER_STOPPED_BURN` | proposed | the stopped pipeline was Relentless; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `PLANNING_BUILD_DAYS_OF_ORDERS_NO_HOME` | proposed | the pipeline's orders now live in the ./pipe control store (2e8cae060a) |
| `PRODUCER_CAPS_DECIDE_EVENT_ROOM` | proposed | the Producer role is disabled (dispatcher_schedule.json) |
| `PROOFCOST_VERIFY_FIRST_DAY_SLIPPED_BASELINE` | proposed | compared Relentless live-proof throughput; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `PROOFYIELD_REPAIR_THREE_OF_THIRTEEN_MEASURED` | ready | Relentless live-proof yield; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `PYDANTIC_CONTRACTS_DESIGN_ONE_SCHEMA_TWICE` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a design pass on RimFlow v3 |
| `REBIND_FIX_OFFBOX_CAP_FULL_HOUSE` | proposed | Relentless agent contracts (rebind); Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `REPLAN_REQUEST_BUILD_CLOSED_RECORD` | proposed | the Producer role is disabled |
| `ROLE_RUNS_ENFORCE_STOP_AT_TWICE_CAP` | proposed | done another way: every role's hard stop is about 2x its measured cost (RIMMANDRAKE_RESTORE_PAUSED_WORK_KEEP_EVERY_SPEND_CAP, dispatcher_schedule.json _run_budget_why), and spend caps go through spend_watchdog.wrap (owner 2026-11-16) |
| `SAMPLE_FILLING_FIX_FOUR_WAKES_PER_CLOCK` | proposed | sample_filling no longer exists in src (git grep: none) |
| `SCHEDULEDOC_CORRECT_PRIORITY_RANK` | proposed | account_pick is advisory (act=recommend, hold [] by owner 2026-11-02); the real order lives in switching_plan |
| `SCRATCHREAP_MUTANTS_FINISH_SERIAL_RUN` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a mutation-run item, no failing behaviour |
| `SCRATCH_REAP_HARDEN_GIT_EDGE_HOLDS` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); unconfirmed adversarial edge cases, no failure seen |
| `SEAT_MEMORY_STANDARD_FALLBACK_1` | ready | a contingency ('if the home-made pieces misbehave'), not work; tmp.mount masked at f573a80751; re-file on a misbehaviour |
| `SEED_CHECK_FIX_WEAK_NAMES_BAD_WORK` | proposed | Relentless E1 seeds and Marker verdicts; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |
| `SLOT_CAP_WIDEN_DESK_WHILE_OWNER_PRESENT` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); his presence at the machine is not an event (owner 2026-10-30) |
| `SLOT_HOOK_MEASURE_REFUSALS_AND_PEAK` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a measurement for the v3 slot allocator tuning, no consumer |
| `SLOT_SITTING_FIX_UNMEASURED_START` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); slot allocator sittings were v3 tuning |
| `SLOT_STREAMS_BUILD_SPLIT_R1_R7` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); v3 allocator stream split, never adopted |
| `SPEND_CENSUS_REFUSE_MISSING_USAGE_NOT_ZERO` | proposed | its consumer arena_spend went with the arena (1f0e666566); sim/spend_census.py is a one-off census script nothing runs, and the ticket itself counted 0 such cases in 7680 real ids |
| `TESTPILOT_FIX_ABORT_WRONG_SCENARIO` | built | Utils/arena/testpilot.py was removed with the arena at 1f0e666566 (owner card 2026-11-05) |
| `TESTPILOT_FIX_LAUNCH_FAIL_HOLDS_BRIDGE` | built | Utils/arena/testpilot.py was removed with the arena at 1f0e666566 |
| `TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND2` | built | Utils/arena/testpilot.py was removed with the arena at 1f0e666566 |
| `TIMERS_PAUSE_DIAGNOSE_WHO_HIT_THE_BRAKES` | proposed | parked by owner card 2026-10-29 ('old workflow, stop now'); a one-off 2026-10-29 forensic |
| `TOKEN_PACE_MEASURE_USAGE_SERIES` | proposed | pool pacing shipped in switching_plan (skill rimflow-operations); its pulse/usage.py series was RimPulse's |
| `UNMEASURED_ROUTES_WIRE_NO_SIX_HOUR_NAPS` | proposed | Relentless's UNMEASURED routes; Relentless retired by the owner 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md) |

## DUPLICATE (6)

| ticket | state at census | evidence |
|---|---|---|
| `CLOSE_SHA_REPAIR_FOUR_ON_ALL_SAINTS` | proposed | into `CLOSE_SHA_REPAIR_EIGHT_ON_LEAP_DAY`: same repair as CLOSE_SHA_REPAIR_EIGHT_ON_LEAP_DAY |
| `CUTCRIT_RESTORE_173_BUILT_MID_SENTENCE` | proposed | into `CRITERIA_TEXT_FIX_CUT_AT_CAP`: the same 160-char criterion cap as CRITERIA_TEXT_FIX_CUT_AT_CAP |
| `QUOTA_ENFORCE_UNUSED_AT_RESET_WASTE` | proposed | into `QUOTA_LEFT_AT_RESET_MEASURE_PER_ACCOUNT`: needs the measurement first |
| `SCRATCHREAP_REVIEW_FINISH_PATH_SHAPE_TAIL` | proposed | into `SCRATCH_REAP_FIX_ROUND_TEN_STILL_FINDS`: the scratch_reap review rounds; CLEANER_SANITY_REVIEW_FINISH_FULL_FILES carried them to round 4 (3bf4cecd5f) |
| `SITECALM_FIX_HIVE_APPEARS_MIDRUN` | proposed | into `DRIVERSITE_FIX_HIVE_HALTS_TWO_MAPS`: the same test-site hive problem |
| `TELEMETRY_STACK_BUILD_AFTER_THE_MOVE` | proposed | into `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED`: the same stack as TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED (validated) |

## VALID_SMALL (1)

| ticket | state at census | evidence |
|---|---|---|
| `ROLE_HEADERS_RETIRE_ENABLED_PROSE` | proposed | built in part at 0e982afe59: no role file states its switch setting any more (selftest_role_headers_state_free.py, red before, green after); producer.md, auditor.md and innovator.md had said enabled while disabled. LEFT OPEN: the clock-time and cap half (18 clock lines, 27 cap lines in seven role files) is prose rework of live role instructions, more than an hour |

## VALID_LARGE (121)

| ticket | state at census | evidence |
|---|---|---|
| `ACCOUNTS_RESTORE_STEVE_LINE_AFTER_BIG_WEEK` | ready | week.conf still points account-plan.service at switching_plan_week_2026-11-05.json, which now carries his 2026-11-17 orders (git 9ae57150a3): removing it would undo them. The standard switching_plan.json has checkpoint_grace_s (RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH) that the live week file lacks, so that feature is not live. Needs: merge the week file into switching_plan.json, then delete week.conf, in one sitting the Conductor watches. Acceptance: systemctl --user cat account-plan.service shows no RM_SWITCH_PLAN and switching_plan.py status shows his 11-17 order and checkpoint_grace_s. |
| `ACCOUNT_KEEPALIVE_VERIFY_STILL_BREATHING` | proposed | a SteveDesktop reading; SteveDesktop is off-limits this run (72 h soak). Deadline: the 30-day refresh window lapses about 2026-11-23. UNMEASURED. |
| `ADVANCEUNTIL_WIRE_PER_TICK_STOP` | proposed | bridge conditions T3: companion C# plus a live acceptance; waits on CONDPROBES_WIRE_ENGINE_READS's live proof |
| `BENCH_WIRE_BACKSTOP_STILL_ON_GOODBYE` | ready | Conductor restart behaviour; belongs with CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM and the 2026-11-18 conductor-restart tickets |
| `BRIDGE_STRANDING_DIAGNOSE_SEVEN_MORE_DRIVERS` | proposed | SteveDesktop testq driver strandings; Steve is off-limits this run |
| `CLOSE_SHA_REPAIR_EIGHT_ON_LEAP_DAY` | proposed | thirteen October closes cite a sha that is not their work; each needs its real commit found and noted (research, ~1-2 h) |
| `CODE_REVIEW_ENFORCE_REVIEWER_NOT_AUTHOR` | proposed | code_review_status mark-clean still takes any caller's mark; enforcing reviewer != author needs an identity source (review_identity.py) wired into mark-clean |
| `CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER` | proposed | new companion capability; waits on CONDPROBES_WIRE_ENGINE_READS's live acceptance |
| `CONDUCTOR_RESET_FIX_KILLED_MID_READ` | ready | work landed (6958dcbf4e) but selftest_conductor_reset_mode.py did not finish in 170 s, alone (exit 124): UNMEASURED; needs a run without the cap |
| `CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM` | doing | doing since 2026-11-02; the parent of the 2026-11-18 conductor-restart tickets |
| `CONDWATCH_BUILD_OWNED_RINGS` | proposed | bridge conditions T5, live |
| `CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH` | doing | SteveDesktop CPU retest after the soak drains; off-limits this run |
| `CRITERIA_TEXT_FIX_CUT_AT_CAP` | proposed | model.CRITERION_TEXT_MAX is still 160 (model.py:338); a schema change on the ledger |
| `CRITIC_CALIB_HARDEN_WALK_AND_HEADS_FALLBACK` | ready | art-critic residuals; not probed this run (UNMEASURED) |
| `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` | ready | work landed 22e48e7f0a, but its live line does not hold: D:\ClaudeWork\rimmandrake\artpipe\registry.jsonl is 70 h old (max 6 h), so rimflow refuses the close; needs the artpipe registry writer read (idle, or broken?) |
| `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE` | ready | retitle: review the C# files code_review_status still lists DIRTY (81 waves landed, last 55c201dd6f) |
| `DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE` | proposed | four Codex round-4 findings on dispatcher.py, unverified; each needs a red test first |
| `DISPATCHER_VERIFY_SAME_SECOND_HANDOFF` | proposed | dispatcher.py handoff verification on whole-second timestamps; needs a same-second test |
| `DOORBELL_ARM_HARDEN_TWO_NARROW_RACES` | proposed | two races in doorbell.py (_disarm_if_mine, take_ring); concurrency work |
| `DOORBELL_DELAY_FIX_FRESH_WINDOW_WAITS` | proposed | fresh-window wake delay; belongs with the conductor-restart work |
| `DRIVERSITE_FIX_HIVE_HALTS_TWO_MAPS` | proposed | test-site hive clearing in the northstar driver; live |
| `EVIDENCE_METRICS_WIRE_ONE_ROW_EVER` | ready | work landed 38c6a169d0 and its selftests pass, but a Relentless lease (gen 1, checking) still carries it, so close is refused; needs the lease released by its supervisor |
| `FIRST_TOUCH_DECIDE_HARNESS_NAMES_A_MOD` | proposed | first_touch.py still holds items naming a mod; deciding whether system repairs are exempt is a design call |
| `FOCUS_ENFORCE_HEADLESS_LAUNCH_ALLOWLIST` | proposed | headless launch allowlist; not built |
| `FOUNDRY_RETIRE_REVIEW_DIRTY_FILES` | proposed | retitle: full-file review of cli.py, priority.py and the rest still DIRTY |
| `GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN` | ready | Windows-side observer; blocked on the TPS overhead test, live |
| `GC_EARLYLOAD_DUMPS_PROBE_SHOW_VALUE_FIRST` | proposed | blocked on the TPS overhead test, live |
| `GOODBYE_CANCEL_FIX_PEER_ATE_THE_NIGHT` | ready | Conductor goodbye restart; belongs with the conductor-restart work |
| `GRANT_RESTORE_CAMPAIGN_WHEN_HE_PLAYS` | proposed | waits for him to start playing (months away, owner 2026-10-24) |
| `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD` | proposed | blocked on the TPS overhead test, live |
| `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP` | proposed | after the health metrics have run |
| `HELPER_RECEIPTS_FOREGROUND_FIX_UNREAD_SKIP` | proposed | helper_receipts.harvest still exists; needs a red test for the unread foreground case |
| `HOOKS_SCANGUARD_WIDEN_FOUR_SIBLINGS_SLIP` | proposed | selftest_block_blind_scan.py has no bash -lc, & , subshell or $(...) case: the four slips are untested; hook parsing work |
| `LEFTOVERS_CHECK_FIX_SAFE_ON_UNSAFE_FOLDER` | proposed | not probed this run (UNMEASURED): needs the leftovers checker read |
| `LIGHTSPEED_WIDEN_112_MODS_NEVER_QUEUED` | ready | testq rollout batches; selftest_testq_coverage.py red on HEAD in this run's batch |
| `LIST_READING_FIX_FILLER_PROVES_NOTHING` | proposed | priority_list entry readings; the Conductor keeps the list (set 2026-11-14, 06b2cf4407) |
| `MODSWAP_FIX_REORDERED_LIST_READS_FOREIGN` | proposed | modset_builder.take_before_copy; needs a red test |
| `NORTHSTAR_SITUATIONAL_ROLLOUT_1` | ready | the every-suite abort pass through testq has not finished; blocked |
| `OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO` | proposed | Codex round-4 findings on ops_watch.py (blind readings as measured zero): each needs a red test |
| `OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME` | proposed | blocked on the TPS overhead test, live |
| `OWNER_CARDS_HARDEN_DECISION_RECEIPTS` | proposed | card receipts; not built |
| `OWN_PRESET_PRUNE_FURNACEHERD_GHOST_KEY` | proposed | JawaBenchHealthCore.cs still names FurnaceHerd; a companion DLL rebuild and deploy |
| `PHONE_SENDS_ENFORCE_STILL_HONOR_SYSTEM` | proposed | no mechanical prereview gate on chat_review.py phone sends |
| `POLLLOOPS_MIGRATE_THE_OTHER_SEVENTY` | proposed | migrate ~70 bridge poll loops; waits on T3/T9 |
| `POLLLOOPS_MIGRATE_TO_UNTIL` | proposed | bridge conditions T9; waits on T3 |
| `PROOF_TIERS_WIDEN_FOUR_FULL_LIST_HOLDOUTS` | proposed | four places assume the full mod list; not probed (UNMEASURED) |
| `QUOTA_LEFT_AT_RESET_MEASURE_PER_ACCOUNT` | proposed | record quota left at each reset over several cycles (days of readings) |
| `REAPER_SESSION_DIRS_MEASURE_END_LINE_YOUNG` | ready | scratch reaper reading; blocked |
| `REBOOT_BREAKGLASS_VERIFY_1` | proposed | needs a Windows reboot of Archmagi; not while detached runs and the Steve soak are live |
| `RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP` | proposed | full-list overhead protocol in game |
| `RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM` | ready | retitle: full-file review of ops_watch.py and the other files still DIRTY after the 2026-11-03 fixes |
| `RESOURCE_SIM_BUILD_WAITS_FOR_REAL_DATA` | proposed | needs 7+ days of readings |
| `RESTARTREQ_GUARD_RENAME_NO_HARDLINK_RACE` | proposed | seat_restart.consume_request fallback race; needs a red test |
| `RETIRED_DONOR_REFS_WIDEN_TO_CODE` | proposed | widen retired_donor_refs.py to .py/.cs; not built |
| `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS` | proposed | the refusal-contract parent; its children T3, T5, T7 are open |
| `RIMMANDRAKE_BUILD_NEUTRAL_CRITERIA_FIXER_WITH_GUARD` | proposed | built at 57b99e45ff; its auto-launch and a fresh rejudge are still owed (2026-11-15 sleeper census row 6) |
| `RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST` | proposed | bridge validation observatory; not built |
| `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE` | proposed | in-game C# scene runner; live |
| `RIMMANDRAKE_EXTEND_PLAYER_TRUTH_SWEEP_LADDER_WAS_ONE` | proposed | trial 2 ran 2026-11-13 (a578a7bc81); the ladder is not built |
| `RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES` | proposed | scan_def_slots reads base defs only; the fix is to read the patched tree (effective_def_lint.py already builds one), with a test on a patch-repointed def |
| `RIMMANDRAKE_FIX_TICKBENCH_WSL_PATHS_UNDER_PYTHONEXE` | proposed | e51e288739 filed or began it; not probed (UNMEASURED) |
| `RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK` | proposed | not built |
| `RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER` | proposed | an inventory; not started |
| `RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS` | proposed | refusal contract T7; not built |
| `RIMMANDRAKE_LEARN_REVIEW_CORRECTIONS_FROM_OWNER` | proposed | a corpus for the findings judge; not built |
| `RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT` | proposed | the preflight spec's parent; its trio is the current build (RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH and successors) |
| `RIMMANDRAKE_PREPARE_FIRST_LOOK_MATRIX_SAVEGAME` | proposed | a savegame standard; live |
| `RIMMANDRAKE_PROPAGATE_REFUSAL_CONTRACT_TO_DOCS` | proposed | CLAUDE.md and standing_rulings carry it (ad403fd090); the two skill lines wait for a curation session |
| `RIMMANDRAKE_RECORD_GATE_REFUSALS_DROP_DEAD_MARKER` | proposed | refusal contract T3: a1c6216002 replaced the dead-marker clause; refusal records not built |
| `RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG` | proposed | jawa/health C# fixes; live |
| `RIMMANDRAKE_REVIEW_SPEED_BATCH_CODE_STILL_DIRTY` | proposed | full-file review of validation_core and the speed_20261112 files |
| `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS` | proposed | not built |
| `RIMMANDRAKE_ROUTE_ART_ROUND_CAP_TO_CRITERIA_FIXER` | proposed | refusal contract T8; not built |
| `RIMMANDRAKE_WAIT_LOAD_READY_UNTIL_CURRENTMAP_SET` | proposed | bridge readiness; needs a live check |
| `RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING` | proposed | he answered; ours to design (2026-11-15 sleeper census row 12) |
| `RIMMASTER_FIX_AGENT_GAME_EVENTS_FILED_AS_OWNER` | proposed | ./game events by a helper recorded as OWNER; needs a read of the 2026-11-08 events and ./game's seat choice (UNMEASURED) |
| `RIMMASTER_FIX_REMOTE_TAKE_HOLDS_LOCK_NOBODY_READS` | proposed | SteveDesktop remote bridge take; Steve is off-limits this run |
| `RIMMASTER_GUARD_WRECKED_LINKS_STATIC_LIST_TRIPS_RATCHET` | proposed | selftest_static_game_state.py exits 1 on HEAD in this run; RM_WreckedLinksProof.cs holds a static list (a C# proof fix and DLL build) |
| `RIMMASTER_MOVE_IMAGE_SKILLS_OUT_PAST_CODE_PATHS` | proposed | skills move; a curation session |
| `RIMMASTER_RESTORE_HOURLY_INSTALL_TIMER_PILE_GREW_UNSEEN` | proposed | art install timer; needs an art-pipeline read (UNMEASURED) |
| `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL` | proposed | an outside-skills assessment |
| `RIMMASTER_WIRE_STEVEDESKTOP_TELEMETRY_FLYING_BLIND` | proposed | SteveDesktop telemetry route; Steve is off-limits this run |
| `RINGPROBES_WIDEN_MESSAGES_RING` | proposed | companion capability; waits on T6 |
| `RINGPROBES_WIRE_EVENT_CURSORS` | proposed | bridge conditions T6, live |
| `ROLE_DUTIES_FIX_CARRY_MISSED_SLOTS` | proposed | role slot carry-over in the Dispatcher; not built |
| `RULINGS_BUILD_STATE_RECONCILER_NEWEST_WINS` | proposed | ruling-vs-state reconciler; not built |
| `RUNNERCLONE_FIX_STRANDED_BY_HISTORY_REWRITE` | proposed | SteveDesktop clones; Steve is off-limits this run |
| `RUN_SELFTESTS_FIX_STDERR_EATS_MARKER` | proposed | Codex round-4 findings on run_selftests.py; each needs a red test |
| `SCAN_MARKED_HARDEN_YOUNG_SIBLING_BLINDS` | proposed | role_launch.scan_marked/procs_of still exist (role_launch.py:3185); needs a red test |
| `SCRATCHREAP_FIX_HUNGRY_FOR_FOUR_GIGS` | proposed | scratch_reap memory peak; not re-measured (UNMEASURED) |
| `SCRATCHREAP_FIX_SELFTEST_BLINDS_OTHER_RUNS` | proposed | concurrent scratch_reap selftests; selftest_scratch_reap timed out at 170 s in this run's batch |
| `SCRATCH_AGE_FIX_FIFTY_SIX_YEARS_YOUNG` | proposed | scratch cleaner oldest_h epoch bug; not probed (UNMEASURED) |
| `SCRATCH_ENACT_REPAIR_SELFTEST_CRUMB_TRAIL` | proposed | enact selftest litter; not probed (UNMEASURED) |
| `SCRATCH_REAP_FIX_ROUND_TEN_STILL_FINDS` | proposed | Codex round-4 findings on scratch_reap.py; each needs a red test |
| `SCRATCH_REAP_SELFTEST_FIX_NEVER_ENDS` | proposed | selftest_scratch_reap still reached no verdict in 170 s in this run (exit 124) |
| `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP` | ready | the BENCH seat-key rename is Phase 2 of the retired-eras index (4b1c4a745c folded BENCH.md only) |
| `SEAT_GOODBYE_FIX_QUEUED_PROMPT_LOST` | proposed | Conductor goodbye; belongs with the conductor-restart work |
| `SEAT_GOODBYE_FIX_REPLACEMENT_DIED_UNREAD` | proposed | Conductor goodbye; belongs with the conductor-restart work |
| `SEAT_MEMORY_PROVE_HARNESS_SLICE_OOM_KILLS` | proposed | rm-harness.slice OOM toast; not built |
| `SEAT_RESTART_FIX_TAKEN_REQUEST_LOST` | proposed | seat_restart edge case; belongs with the conductor-restart work |
| `SEAT_RESTART_REPAIR_TORN_TAIL_AT_GOODBYE` | proposed | seat_restart edge case; belongs with the conductor-restart work |
| `SEAT_SYNC_FIX_LATE_SAVE_DELETED_PARK` | proposed | seat_sync park race; needs a red test |
| `SELFTEST_CLOCK_BUILD_INJECTED_TIME` | proposed | an injected clock across many selftests |
| `SELFTEST_SLOW_FOUR_SHRINK_BY_SPLIT` | proposed | split four ~600 s selftests; mod selftests, nightly held |
| `SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD` | proposed | test-site quiet on Steve chain runs; live |
| `SLOTS_RENAME_FOUNDRY_KEY_RELENTLESS_READS_IT` | proposed | Phase 2 of the retired-eras index (slot_rules FOUNDRY key) |
| `STEPCALLS_MIGRATE_WHERE_VERDICTS_HOLD` | proposed | migrate ~255 callers in batches |
| `STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH` | proposed | SteveDesktop hardware; off-limits this run |
| `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` | ready | SteveDesktop RAM test owed; off-limits this run |
| `STEVE_DEPLOY_FIX_AURORA_TYPE_MISSING` | ready | 92447583b5 named the cause (a stale WeatherSuite DLL on Steve); the fix is on SteveDesktop, off-limits this run |
| `STEVE_RETEST_TIMER_RETIRE_WHEN_CPUS_SPEAK` | ready | steve-cpu-retest.timer is still enabled on Archmagi; retire it once CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH reports |
| `TAILSTATE_SHRINK_WHEN_SPOOL_FULL_BLOATS` | proposed | telemetry ingest; needs a red test |
| `TELEMETRY_DUPLICATES_RETIRE_AFTER_QUIET_WEEK` | proposed | fold duplicate telemetry transports; not built |
| `TELEMETRY_FAKE_DEPLOYS_EXCISE_NOT_REWRITE` | proposed | remove 159 fake rows from the live telemetry store |
| `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES` | proposed | four telemetry edge cases; each needs a red test |
| `TERRAIN_BATCH_FIX_READBACK_REFUSES_PLOTS` | proposed | jawa/set_terrain_batch read-back; live |
| `TRACE_MKDIR_HARDEN_STAT_OUTLIVES_IT` | proposed | known_results.py shim; selftest_known_results.py red on HEAD in this run's batch |
| `VITALS_PROOF_ENFORCE_TIER_DECLARED` | proposed | a live proof's tier declaration; not built |
| `WAKE_LIST_FIX_OLD_MAIL_MARKED_LATE` | proposed | seat_restart wake list; belongs with the conductor-restart work |
| `WARMTIMER_HARDEN_SPARE_LIVE` | proposed | claude-account-warm.timer is not on Archmagi (systemctl lists none): it is SteveDesktop's, off-limits this run |
| `WINSTAGE_CULL_THREE_GIGS_PER_KERNEL` | proposed | selftest_winstage rsync scope; needs a timing probe |

## LIVE_ONLY (38)

| ticket | state at census | evidence |
|---|---|---|
| `AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE` | built | built; owes its live proof; the game is off-limits this run |
| `BRIDGETOOLS_DLL_REBUILD_THREE_TOOLS_MISSING` | ready | a JawaBench DLL rebuild and deploy; deploy touches the game, off-limits this run |
| `BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN` | built | built at fe486e20b2; remaining criteria live |
| `BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE` | built | built; work landed 0bc98a3360, its 1 selftest(s) green on HEAD; remaining criteria live |
| `BRIDGE_LOCK_HARDEN_ALIVE_MEANS_A_PID` | built | built at 951f8054bd; remaining criteria live |
| `BRIDGE_RECONCILE_WIRE_CLOSED_NOT_CURED` | built | built; work landed 940aaef989, its 1 selftest(s) green on HEAD; remaining criteria live |
| `BRIDGE_STALL_DIAGNOSTIC_1` | built | built; owes a fresh companion build and a live proof (32802cb7f9) |
| `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` | built | built; owes its live proof |
| `BRIDGE_TPS_CAPTURE_FIXES_1` | validated | validated; work landed e0be5c81b8, its 1 selftest(s) green on HEAD; remaining criteria live |
| `BRIDGE_TPS_REGULAR_REPORT_1` | built | built; work landed d7a9fe9ea2, its 2 selftest(s) green on HEAD; remaining criteria live |
| `BRIDGE_TPS_REVIEW2_FIXES_1` | built | built; owes its live proof |
| `COLDLOAD_PROVE_DEFLOADCACHE_HALF_INSTALLED` | ready | a cold-load trial in the game |
| `COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT` | validated | validated; its remaining criteria are live |
| `CONDPROBES_WIRE_ENGINE_READS` | built | built; work landed 54558735f9, its 1 selftest(s) green on HEAD; remaining criteria live |
| `EFFECTIVE_DEF_LINT_WIDEN_PAST_DURASTEEL` | built | built; owes its remaining criteria |
| `EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS` | built | built for the C0-C5 overhead protocol, which is live |
| `FIXTURES_FIX_REST_STILL_COMPRESSED` | built | built; work landed fb1f414ca6, its 3 selftest(s) green on HEAD; remaining criteria live |
| `FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS` | built | built at e6c10a36b4; remaining criteria live |
| `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME` | ready | blocked on in-game metrics (TPS overhead test) |
| `HEALTH_METRICS_PROVE_EIGHT_WRITTEN_UNTESTED` | ready | deploy and measure in game |
| `JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT` | built | built; work landed 5981ca76dd, its 3 selftest(s) green on HEAD; remaining criteria live |
| `KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES` | built | built at b094393713; remaining criteria live |
| `LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE` | built | built at cbec3e5b54; remaining criteria live |
| `MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL` | built | built; work landed 768d5579de, its 2 selftest(s) green on HEAD; remaining criteria live |
| `MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH` | built | built at ec78d34fbd; remaining criteria live |
| `NORTHSTAR_COMPANION_GAPS_1` | validated | validated; remaining criteria live |
| `PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT` | validated | validated; remaining criteria live |
| `PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET` | built | built; work landed 9a24b0562b, its 1 selftest(s) green on HEAD; remaining criteria live |
| `PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND` | built | built; remaining criteria live |
| `RIMMANDRAKE_FIX_JAWABENCH_AWARENESS_INSTALL_CRASHES_START` | proposed | a game-start crash on 2 of 4 launches |
| `SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB` | proposed | needs a fresh DefDump capture from the game |
| `STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES` | built | built; its proof is on SteveDesktop |
| `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED` | validated | validated; the rm-telemetry-* timers run; remaining criteria live |
| `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO` | validated | validated; remaining criteria live |
| `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME` | built | built; work landed da7aa72c65, its 3 selftest(s) green on HEAD; remaining criteria live |
| `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` | built | built; remaining criteria live |
| `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL` | built | built; work landed 21a392bc9b, its 1 selftest(s) green on HEAD; remaining criteria live |
| `WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF` | built | built; work landed 291d5bb4dc, its 2 selftest(s) green on HEAD; remaining criteria live |

## KEEP (7)

| ticket | state at census | evidence |
|---|---|---|
| `OPS_PLAN_LIST_FIX_VMIV` | ready | the live item of the open PLAN_DISTRESS alarm (priority list closed_entry since 2026-11-13); the Conductor keeps that list |
| `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ` | ready | the live item of the open SCRATCH_DIRTY_END alarm |
| `OPS_SCRATCH_DIRT_MEASURE_AT_START_SANF` | ready | the live item of the open SCRATCH_DIRTY_START alarm |
| `OPS_SCRATCH_OUTSIDE_READING_RESTORE_WLTC` | ready | the live item of the open SCRATCH_OUTSIDE_BLIND alarm (filed 2026-11-18 22:44Z) |
| `OPS_WRAPUP_DRAIN_DEBRIS_PILES_UP_RWZN` | ready | the live item of the open WRAPUP_DEBRIS alarm (filed 2026-11-18 22:30Z) |
| `STEVE_FILLER_MONITOR_FAIL_FINDINGS` | ready | a standing host the testq filler files its FAIL findings onto |
| `STEVE_LANE_MONITOR_PAUSE_FINDINGS` | ready | a standing host for SteveDesktop lane pauses (2f74ae363d keeps it open on purpose) |

## NEEDS_HIM (2)

| ticket | state at census | evidence |
|---|---|---|
| `DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING` | proposed | Archmagi D: NVMe throws corrected PCIe AER (ops_watch counts it, 90aa0cc741): will you reseat the drive at a sitting, or leave it monitored? |
| `RIMMASTER_SETTLE_HANDOFF_CULL_AGE_TWO_RULINGS_DISAGREE` | proposed | two of his rulings give different handoff cull ages (project handoff.py 30 days, owner 2026-09-18, vs Lodestar's): which one stands? |

## OUT (2)

| ticket | state at census | evidence |
|---|---|---|
| `MODCHECK_SUITE_CORRECTIONS_1` | ready | mod-suite content (12 mod suites), out of scope |
| `RIMMASTER_TRIAGE_MOD_OWED_CENSUS_120_STILL_UNREAD` | proposed | triage of 120 mod-content items, out of scope |

## Findings and builds of this run

- `RIMMANDRAKE_SCOPE_SELFTEST_LEDGER_READS_PREFLIGHT_LOG_TRIPS` (filed and fixed, 1fe595f83e): `selftest_reconcile.py`
  and `selftest_built.py` read every `*.jsonl` in their case dir as ledger events, including the ticket preflight's
  `refusals/preflight_runs.jsonl`; 5 cases red with `KeyError: 'event'` on HEAD, all green after.
- `selftest_prooflint_at_filing.py` check 7 counted call text and read 2 of 3 doors after the preflight gate began
  routing `file` (31c94dd37a); fixed to check each door (e6ab733c03), a mutant with the close door removed is caught.
- `ROLE_HEADERS_RETIRE_ENABLED_PROSE`, switch part (0e982afe59): producer.md, auditor.md and innovator.md said
  "enabled" while their schedule rows are disabled; no role file states its switch now (`selftest_role_headers_state_free.py`).
- The live account plan is the week file (`week.conf` -> `switching_plan_week_2026-11-05.json`); the standard
  `switching_plan.json` holds `checkpoint_grace_s`, which the live service therefore does not read. Noted on
  `ACCOUNTS_RESTORE_STEVE_LINE_AFTER_BIG_WEEK`.
- `items/` glob drift: `RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER` (done) had live prose; moved to
  `items/closed/` (4eee6199f5, fe7c4ea9eb); `selftest_items_glob_live.py` 7/7.
- Reds seen on HEAD in this run with no fix here: `selftest_focus_cap.py` ("the refused claim wrote no event"),
  `selftest_known_results.py` (planted case), `selftest_static_game_state.py` (`RIMMASTER_GUARD_WRECKED_LINKS_STATIC_LIST_TRIPS_RATCHET`),
  `selftest_scratch_reap.py` and `selftest_conductor_reset_mode.py` (no verdict in 170 s: UNMEASURED).
- `RIMMANDRAKE_DECIDE_GUARDS_OWED_BY_LANDED_OLD_FIXES` (filed for the Conductor): the 69 DONE, GUARD OWED rows,
  and why most of their deaths were not the fix.
- Two DONE rows could not close and moved to VALID LARGE: `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` (its live
  line fails: the artpipe registry is 70 h old) and `EVIDENCE_METRICS_WIRE_ONE_ROW_EVER` (a Relentless lease still
  carries it).

## What the ledger holds after this run [measured, ledger replay 2026-11-18 ~4:20 PM PST]

29 DONE rows closed with their sha (4 with a live line); 103 dropped (73 DEAD, 30 CLEARED, dependents released); 6
superseded; every open row (VALID LARGE, LIVE ONLY, KEEP, NEEDS HIM, DONE GUARD OWED, VALID SMALL) carries an
`OLD-ERA SWEEP 2026-11-18` note with its evidence. Item titles were not rewritten (rimflow has no retitle verb); the
note says what each needs in today's words.
