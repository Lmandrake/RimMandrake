# Sweep of the open pipeline and machine tickets, 2026-11-27

Item: `RIMMANDRAKE_SWEEP_PIPELINE_TICKETS_HE_ORDERED_ONE_MOD_ONLY`. The owner's order, about 9:47 AM PST 2026-11-27: "Please
gracefully throttle down game development to a single advancing mod. Refocus on pipeline ticket cleanup."

One pass, started 9:55 AM PST, page written 10:26 AM PST 2026-11-27. Each ticket has one class and its evidence. The sweep's base is the
table of the day before, `design/specs/2026-11-26-parked-pipeline-tickets/table.md`. That table classed 53 parked tickets
of these homes. This sweep acts on the calls that the table left open where the brief orders the act (a check moved to
the small list, a park lifted with the obvious answer). It re-reads every ticket against today's ledger.

## The set

- The 33 old tickets in `pipeline:` and `machine:` homes (`list_home.py list`, 9:55 AM PST).
- The pipeline-machinery tickets that `list_dispatch.py status` (9:50 AM PST tick) shows as chain_stop, adopt_too_heavy,
  blocked, routed to the conductor, or waiting on a Conductor act.
- The pipeline-machinery lines of `cli.py queue CONDUCTOR --owed --all`.
- Left out by the brief: `mod:` and `game:` homes, faction work, held mods, and the owner's five acts. The art, flyer, sea,
  sun and FlowWorks lines of the Conductor's queue are of that kind.

## Count by class

| class | tickets |
|---|---|
| DONE in this run (closed by recording a pass that the evidence already held) | 2 |
| DONE before this run | 2 |
| STALE, dropped | 1 |
| NOT WORTH THE TOUCH, dropped | 1 |
| KEEP, with an act in this run (un-parked or un-blocked for the ticket lane: 3; half of a check moved to the small list: 1; home corrected: 1) | 5 |
| KEEP, no act (full list only 10; his act, his park or his word 6; a date, the pick of 2026-12-04 or a program ends it 16; raid pause, standing items and a Conductor read after a mod run 5) | 37 |
| CONDUCTOR CALL (listed below) | 14 |
| total | 62 |

## Tickets

| ticket | class | act (sha or command) | left for the Conductor |
|---|---|---|---|
| `HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE` | KEEP (full list only) | none; stays parked for the integration phase | The retained 59 MB per reload is a full-list finding (8 MB on 14 mods). A1 to A3 run on small tiers, but they can only give the baseline: naming the retainers needs A4 to A6 on the big tiers. Nothing for the Conductor. |
| `HEAP_READ_BISECT_ROWS_NAME_THE_RETAINERS` | KEEP (full list only) | none; stays parked | It reads the rows of HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE. |
| `REBOOT_BREAKGLASS_VERIFY_1` | KEEP (needs him) | home corrected machine:SteveDesktop -> machine:Archmagi: a663007c9a | It needs a Windows reboot of Archmagi at a moment he names, tested from his phone over cellular (his card 2026-09-19). That is a physical act, not one of his five acts. |
| `DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING` | KEEP (his physical act) | none; dated wait to 2026-12-10 stays | His hands reseat the drive; `ops_watch.py whea-quiet` closes the ticket 72 h after that. |
| `WARMTIMER_HARDEN_SPARE_LIVE` | KEEP, un-parked | un-blocked: 4bb9c380d3 | The old owner-card park is lifted with the obvious answer: make the warm skip the live login. Evidence: on SteveDesktop, `claude-account` line 842 skips the live login only when a claude process runs. The fix lands in the claude-remote-control repo, from Archmagi. The ticket lane takes it. |
| `BRIDGE_TPS_CAPTURE_FIXES_1` | DONE | C3 recorded as a pass from the 2026-10-10 full-list run (autostart proven, overhead stated) and the 2026-11-26 lane cold launches: 01003a7eef | none |
| `BRIDGE_TPS_REVIEW2_FIXES_1` | KEEP (full list only) | none | C4 is the full-list overhead protocol (MUST 17): 3 restarts and an overnight reconstruction. It is the same measurement as RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP; both wait for the integration phase. |
| `EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS` | KEEP (full list only) | none; stays parked | A1 is proven only inside the full-list C0-C5 run. |
| `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD` | KEEP (full list only) | none; stays parked | It waits on the full-list overhead test. |
| `HEALTH_METRICS_PROVE_EIGHT_WRITTEN_UNTESTED` | KEEP (full list only) | none; stays parked | It deploys only after the full-list overhead test. |
| `OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME` | KEEP (full list only) | none; stays parked | It waits on the full-list overhead test. |
| `RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP` | KEEP (full list only) | none; stays parked | The C0-C5 protocol is full-list work. |
| `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` | KEEP (half moved to the small list) | A1 re-levelled L4 -> L2 on a small list and passed from the bundle run of 2026-11-25; A2 re-levelled L4 -> GREEN-FULL: 41772e9f40, 5f0ef2336d; parked: 58d8b0ce34 | Only A2 is left. Foreign-thread rejects come from other mods' threads, so only the full list decides A2 (integration phase). |
| `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL` | KEEP (full list only) | none | A1 passed on the small list. A2 is GREEN-FULL (300 or more mods) by its text. |
| `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP` | KEEP (raid pause) | none | Only A10 is left, and it fires a drop-pod raid. Raid tests are paused (`raid_pause.py show`). |
| `THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER` | KEEP (raid pause, no fixture) | none | A5 fires a raid (paused). A2 needs a pawn with two candidate texture packs, which no small list holds. |
| `FLYERFRAMES_PROVE_JOINT_SESSION` | KEEP (his act 1) | none | A live flight test of a flyer is one of his five acts. His sitting of 2026-11-27 12:39 AM PST ended NOT A PASS on Skinflap; that is mod work (RIMMANDRAKE_REDRAW_SKINFLAP_FLUTTER_BUTTERFLY_NOT_SAME_PICTURE). |
| `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` | DONE | A1 and A2 re-levelled L4 -> L2 (check text unchanged; L4 was retired FOUNDRY's tag on agent checks), built sha f11aef63d5 (the build the lane passed; old fd2375d54c is not on origin/main), then the lane pass J20261125T204038Z-3c75d6 recorded: 1e920c0922, 523b687065, a6902c262d | none |
| `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` | KEEP (dated wait) | none; wait to 2026-11-30 stays | The Conductor's ruling of 2026-11-24 puts the cutover on the 2026-11-29 study. Its `adopt_too_heavy` stop: the acceptance script takes more than 120 s, so the tick does not adopt it as an outcome check. That is right while the study decides the cutover. |
| `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` | KEEP (his act 3) | none | It needs a real EK holder run. EK is at his walk (his act 3). |
| `PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE` | KEEP (his park) | none | Parked by his words of 2026-10-31: "Once my live playtesting is the actual bottleneck we will reconsider." It has a design of record, so it is not a Pre-Design Concept. |
| `RIMMANDRAKE_INGEST_HELD_LOOK_DEFECTS_WHEN_LADDER_REGENERATED` | STALE | dropped: 13b57e7bde | none. His card of 2026-11-14 ("Per mod, as it advances") made the placement of a mod's held statements in its test table the ingest. All four advancing mods placed theirs. The acceptance ("empty the holding store") now conflicts, because each mod's preflight reads that store. |
| `RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION` | KEEP (dated wait) | none | Batches one and two and the ten contradictions are done. The prompt diet waits for his rule-file length review (2026-12-05). |
| `RIMMANDRAKE_EVAL_CRYSTALLIZE_SKILL_ONCE_AFTER_EDITS_SETTLE` | KEEP (dated wait) | none | It waits for a fact: the end of the skill edits. His word of 2026-11-24 was "not finished", and the weekly pass still edits the skill. |
| `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP` | CONDUCTOR CALL | none | Steps 1 and 2 are done and hold. Step 3 is his hold of 2026-11-03 ("3 hold for later ... Let's not break ourselves for name correctness"). |
| `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING` | KEEP (program ends it) | none | Its check fails only on RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY. The list_effect tick closes it after the study. |
| `RIMMANDRAKE_STUDY_WHAT_ONE_WEEK_OF_MODS_TAUGHT_ON_NOV_TWENTY_NINE` | KEEP (dated) | none | Owed on 2026-11-29. |
| `RIMMANDRAKE_VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO` | KEEP (his word) | none | The Conductor already marked it ASK HIS (3:25 AM PST 2026-11-27). His card answer of 2026-11-18 ("let's do it carefully. We will need artifacts that let us deeply see what was chosen") is concrete evidence against deleting before he reads the pages. It deletes no file of ours by program. |
| `OWNER_CARDS_HARDEN_DECISION_RECEIPTS` | KEEP (program ends it) | none | The list_effect tick closes it when the 14-day census reads 0, from 2026-12-04. |
| `COLDLOAD_PROVE_DEFLOADCACHE_HALF_INSTALLED` | KEEP (full list only) | none | It is a full-list cold-load trial. A small list loads in about 22 s, which leaves nothing to cache. |
| `RIMMANDRAKE_REFUSE_OWNER_DEFECT_CLOSE_WITHOUT_REGRESSION` | KEEP, un-parked | un-blocked: d3bcb1f65f | The block cited his ruling of 2026-11-12 (store look defects until the ladder is regenerated). His card of 2026-11-14 ("Per mod, as it advances") answered that ruling, so the block's cause has ended. Its acceptance test fails on today's code, as its first note says it should. The ticket lane takes it. |
| `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME` | KEEP, un-blocked | un-blocked: 81d1a69986 | The full-list block was wrong: A1 runs on the minimal list. Its predecessor (companion with JawaBenchSessionHealth.cs) is met: ArchBig's deployed JawaBench.BridgeTools.dll (10:04 AM PST 2026-11-27) holds `privateMB` and `SessionHealth`. It owes a class guard (the fix died once). The ticket lane takes it. |
| `STEVE_FILLER_MONITOR_FAIL_FINDINGS` | KEEP (standing host) | none | A standing host by design ("Do not close while the filler runs"). Its new UNTRIAGED findings are Pyrelands FAIL rows (shore ring, ash fall off, ambient ash off, run-62, 2026-11-27); they are mod work of Pyrelands. |
| `OPS_STEVE_UNSTICK_UNCLAIMED_ETBS_JTIY` | KEEP (program ends it) | none | Cleared at 8:37 AM PST 2026-11-27 (reading 0.0). The 24-hour check can close it from 5:00 AM PST 2026-11-28. |
| `STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_JPMKTL_R3` | CONDUCTOR CALL | none | It is a cause ticket by design (lane_ticket.py: "Ending an incident never ends the ticket: the ticket waits on its cause"), blocked between incidents, so no run ever works the cause. See the calls below. |
| `STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_YVBFTB` | CONDUCTOR CALL | none | The same, and its cause returned: incidents on 2026-11-26 and 2026-11-27 (33 min unowned, 40 min impact). Its text reads IDLE_EMPTY while jobs run: "lane RUNNING again ... but no DONE+canary job since". See the calls below. |
| `RIMMANDRAKE_KEEP_ROLE_NOTES_ON_ONE_LIVE_ITEM` | KEEP (standing notice) | none | It is the standing item of the role notes. It owes no work. |
| `RIMMANDRAKE_SORT_OLD_BUILT_ITEMS_CHECK_REVERTS_BEFORE_CLOSING_212` | CONDUCTOR CALL | none | It is parked by the Conductor until he reads the old-tickets page. See the calls below. |
| `RIMMANDRAKE_REVIEW_RULE_FILE_LENGTH_CEILING_HE_LEFT_OFF` | KEEP (dated) | none | His card of 2026-11-21: "Leave it, review later". It is owed on 2026-12-05. |
| `RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD` | CONDUCTOR CALL | none | The work is done and kept (`list_home.py`). What is left is the Conductor's showing of the page. See the calls below. |
| `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` | KEEP (dated) | none | It guards a real trigger: the 7-day measurements, read on 2026-12-04. |
| `RIMMANDRAKE_BUILD_ONE_LANDING_COMMAND_215_FORM_REFUSALS` | KEEP (waits on the pick) | none | It waits on the pick of RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE. |
| `RIMMANDRAKE_BUILD_VISIT_AND_CYCLE_KITS_SEVENTEEN_COPIES_TODAY` | KEEP (waits on the pick) | none | The same. |
| `RIMMANDRAKE_BUILD_ONE_TEST_CALL_PARENT_FIX_AND_FAULT` | KEEP (waits on the pick) | none | The same. |
| `RIMMANDRAKE_GATHER_ALARM_FACTS_BY_PROGRAM_MOST_END_ACKED` | KEEP (waits on the pick) | none | The same. |
| `RIMMANDRAKE_MOVE_STAGES_BY_PROGRAM_REVERSES_A_WRITTEN_NEVER` | KEEP (waits on the pick) | none | The Conductor ruled "not now" on 2026-11-24; its next look is the read of 2026-12-04. |
| `RIMMANDRAKE_SPLIT_ACTUATOR_OUT_SO_OLD_ENGINE_CAN_GO_AFTER_FIRST_REAL_SWITCH` | CONDUCTOR CALL | none | Its gate is a clean switch on both machines. The wait ends 2:00 PM PST today. See the calls below. |
| `RIMMANDRAKE_GIVE_ONE_MOD_A_DIGEST_HOOK_SO_A_DIRTY_RESET_CAN_SHOW` | NOT WORTH THE TOUCH | dropped: 90aeb978d6; `record:` line on design/specs/2026-11-23-bridge-v2/polish.md | none. No mod of ours has a digest hook (41 loaded, 0 hooked), so no scene reaches that leg, and the offline case `a_dirty_mod_state_changes_the_reset_digest_and_stops_the_repeat` holds the promise. Building a mod hook only to prove a bridge row is a touch that no bar needs (chain_stop at 2 runs). |
| `RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO` | CONDUCTOR CALL | none | The go is done; the Fable Designer ran. What is left is the Conductor's read of the readiness list (row 23, at the 0.1.0 lock). See the calls below. |
| `RIMMANDRAKE_RULE_NEW_MACHINERY_GETS_BLIND_REVIEW_FILED_BY_ITS_RUN` | CONDUCTOR CALL | none | Its trigger is the report of RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX. See the calls below. |
| `RIMMANDRAKE_BUILD_FIVE_SCRIPTS_FROM_SCAN_ONE_BUNDLE_AFTER_ONBOARDING` | CONDUCTOR CALL | none | Its trigger has happened: the onboarding repair landed at bd590ba35f. See the calls below. |
| `RIMMANDRAKE_BRING_PIPELINE_FORECAST_HE_ORDERED_NO_PAUSE` | CONDUCTOR CALL | none | His words since change the question. See the calls below. |
| `RIMMANDRAKE_BUILD_LANE_SWEEP_NO_STATE_THAT_NOTHING_ENDS` | CONDUCTOR CALL | none | Its trigger has happened (bd590ba35f). See the calls below. |
| `RIMMANDRAKE_THROTTLE_GAME_WORK_WHEN_REPAIRS_END_ROOM_SHORT` | CONDUCTOR CALL | none | His order of 9:47 AM PST today did the throttle. See the calls below. |
| `RIMMANDRAKE_ASK_STEVEN_DRAWDOWN_TUESDAY_HE_DECIDES_THEN` | KEEP (dated) | none. A dated wait was refused: a wait may not name the Conductor, and a proposed item cannot wait. The refusal was resolved as not worth the touch, because the title carries the date | The Conductor asks him on Tuesday. |
| `RIMMANDRAKE_ROUTE_REVIEWS_PROVEN_TICKETS_TO_CODEX_ROOM_SHORT` | CONDUCTOR CALL | none | A promise to him. Its premise "while the Claude room is short" changed at 9:43 AM PST today. See the calls below. |
| `RIMMANDRAKE_ORDER_TEN_SLOW_ACTION_FIXES_PAGE_FILED_NONE` | CONDUCTOR CALL | none | "I will pick the order" is the Conductor's promise. See the calls below. |
| `RIMMANDRAKE_REPAIR_ONBOARDING_LAUNCH_SO_BUNDLES_FILL_MEDIAN_ONE` | KEEP (dated wait) | none | Part 3 needs a pipeline home with 5 ready old tickets. After this sweep, `pipeline:operations` may reach that count, but no other home does (see the count below). |
| `RIMMANDRAKE_DECIDE_PYRELANDS_LEDGER_PILOT_TEN_TICKETS_NO_ROUTE` | KEEP (Conductor, after a mod run) | none | It waits on the end of the Pyrelands 0.2.0 build run. |
| `RIMMANDRAKE_RECORD_HIS_ANSWERS_ON_SIX_W48_SKILL_MOVES` | KEEP (his word) | none | He was reluctant on 2026-11-26 while the global CLAUDE.md is crystallized. That is evidence against taking the obvious answer. |
| `RIMMANDRAKE_UNPARK_PIPELINE_TICKETS_NO_HOME_HAS_FIVE_READY` | DONE before this run | none | Closed at 7962a3b566. Its table `design/specs/2026-11-26-parked-pipeline-tickets/table.md` is this sweep's base. |
| `RIMMANDRAKE_TELL_ONBOARDING_CAUSE_FIRST_WHEN_REPAIR_RUN_ENDS` | DONE before this run | none | Closed at 67a74e9db1. |

## Calls for the Conductor

Each call gives the question, the obvious answer, the evidence and what a wrong call costs. None of them is one of his
five acts.

- `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP`. Question: close the item on steps 1 and 2, and drop step 3? Obvious
  answer: yes. Evidence: steps 1 and 2 hold and their test passes (run of 2026-11-26). Step 3 is his hold of 2026-11-03
  ("3 hold for later ... Let's not break ourselves for name correctness"), and nothing else is owed. Wrong call costs:
  a seat key that keeps an old name; a later rename is a new ticket.
- `STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_JPMKTL_R3` and `STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_YVBFTB`. Question:
  should a lane-cause ticket that is seen in two incidents be offered to the ticket lane between incidents? Today the
  steward blocks it, and only the next incident lifts the block. Obvious answer: yes, a cause seen twice gets one
  Workshop run. Evidence: `lane_ticket.py` says "Ending an incident never ends the ticket: the ticket waits on its
  cause", and nothing works the cause while the block holds. YVBFTB had incidents on 2026-11-26 and 2026-11-27 (40 min
  impact the second time). Its text reads IDLE_EMPTY while jobs run. Wrong call costs: one run on a cause that heals by
  itself (small); left as it is, a returning cause is never worked. This is a change to the lane's design, so it is
  your ruling.
- `RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD` and
  `RIMMANDRAKE_SORT_OLD_BUILT_ITEMS_CHECK_REVERTS_BEFORE_CLOSING_212`. Question: close GROUP now, and re-shape SORT
  before you relaunch it? Obvious answer: yes to both. Evidence: GROUP's work is done and kept (`list_home.py`), and its
  own DO line says to ask him nothing. SORT's run of 2026-11-24 measured that "close the 212 by evidence" cannot be done
  as written: all 355 items owe a criterion, and a 55-minute revert search gave no output. Wrong call costs: a relaunch
  as written spends about 2 h and closes nothing (measured).
- `RIMMANDRAKE_SPLIT_ACTUATOR_OUT_SO_OLD_ENGINE_CAN_GO_AFTER_FIRST_REAL_SWITCH`. Question: after 2:00 PM PST today, was
  the lukas-to-system switch clean on both machines? Obvious answer: read `./acct measures` and SteveDesktop's account.
  If the switch was clean, run `list_dispatch.py clear` for one Work run. Evidence: the wait text of 2026-11-26. Wrong
  call costs: deleting the old engine before a clean switch removes the only undo (`./acct driver old`).
- `RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO`. Question: close the item, and move its one open row to
  the mod? Obvious answer: yes. The go is done. Row 23 (count the stage-6 checks against `ingame_cap_tokens` when 0.1.0
  locks) is a step of the mod's own pipeline. Evidence: the run's note of 7:37 PM PST 2026-11-26. His order of 9:47 AM
  PST today keeps one mod advancing, so which mod advances decides when row 23 matters. Wrong call costs: little; the
  readiness list reads row 23 again either way.
- `RIMMANDRAKE_RULE_NEW_MACHINERY_GETS_BLIND_REVIEW_FILED_BY_ITS_RUN`. Question: launch it now? Obvious answer: yes. Its
  trigger is met: `RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX` is done. It is pipeline work, which is the owner's
  focus from today. Wrong call costs: new pipeline scripts keep landing with no blind read (84 of 88 in 7 days had no
  recorded read, note of 2026-11-27).
- `RIMMANDRAKE_BUILD_FIVE_SCRIPTS_FROM_SCAN_ONE_BUNDLE_AFTER_ONBOARDING` and
  `RIMMANDRAKE_BUILD_LANE_SWEEP_NO_STATE_THAT_NOTHING_ENDS`. Question: launch both now? Obvious answer: yes. Both wait
  for "after the onboarding repair lands", and it landed at `bd590ba35f`. Wrong call costs: one bundle of small script
  tickets, and one large build of the lane sweep (on the lane's files, so not in parallel with another lane build).
- `RIMMANDRAKE_THROTTLE_GAME_WORK_WHEN_REPAIRS_END_ROOM_SHORT`. Question: close it? Obvious answer: yes. His order of
  9:47 AM PST today did the throttle, and the control acts ct_000271 to ct_000273 (9:48 to 9:49 AM PST) carried it out.
  His word of 9:43 AM PST says the throttle for lack of room is not needed. What is left is to tell him the pace chosen.
  Wrong call costs: none; the item is a promise to tell him.
- `RIMMANDRAKE_BRING_PIPELINE_FORECAST_HE_ORDERED_NO_PAUSE`. Question: does his order of 9:47 AM PST answer it? Obvious
  answer: give him the one-line Operations forecast for the new pace, then close. Evidence: the question compared
  "continue" against "pause game and mod work", and he has now chosen a third pace (one advancing mod). Wrong call costs:
  one line he did not need.
- `RIMMANDRAKE_ROUTE_REVIEWS_PROVEN_TICKETS_TO_CODEX_ROOM_SHORT`. Question: keep the Codex route now that the room can be
  refilled on demand (his word of 9:43 AM PST)? Obvious answer: keep it. His words of 2026-11-26 ask for a review of
  every new pipeline script, and Codex is a second model, whatever the room. Wrong call costs: a review spent on a script
  that was already clean.
- `RIMMANDRAKE_ORDER_TEN_SLOW_ACTION_FIXES_PAGE_FILED_NONE`. Question: the order. Obvious answer: the order that the item
  names (row 2, the ticket lane's outcome checks; row 3, the pipeline tick), then the page order. File each with its
  acceptance test. Wrong call costs: a slower repair queue until the slow actions go.
- His acts at the desk, one sitting: `DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING` (reseat the drive) and
  `REBOOT_BREAKGLASS_VERIFY_1` (a reboot of Archmagi while he tests break-glass from his phone). Both are physical. Bring
  them to him together.

## What this sweep changed that you should know

- Three criteria re-levelled from L4 (the owner level) to agent levels. Retired FOUNDRY set L4 on checks that agents
  run; its own note of 2026-10-12 says "nothing of the owner's".
  - `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` A1 and A2: L2, check text unchanged.
  - `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` A1: moved to the small list, L2.
  - `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` A2: GREEN-FULL, left for the integration phase.
  - Undo: `rimflow implemented <ID> --criteria-file` with the old lines.
  - Yesterday's table called this re-level a looser bar. This sweep read it as the correction of a wrong tag: the
    observed fact that each check asks for is the same. If you read it as a looser bar, undo it.
- Two old built shas (`fd2375d54c`, `6721b216a761`) are not on origin/main. The FOUNDRY era's history was not kept, so
  the re-implementation named `f11aef63d5`, the build that the lane passed.
- `BRIDGE_TPS_CAPTURE_FIXES_1` C3 was already proved. The full-list run of 2026-10-10 is recorded on
  `BRIDGE_TPS_REVIEW2_FIXES_1` C4, and the 2026-11-25 bundle refusal missed it.
- After this sweep, `pipeline:operations` offers 4 ready old tickets (`HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME` is
  new), `pipeline:ledger` offers 1 and `machine:accounts` offers 1. No pipeline home reaches 5. Part 3 of
  `RIMMANDRAKE_REPAIR_ONBOARDING_LAUNCH_SO_BUNDLES_FILL_MEDIAN_ONE` still waits.

## Not tested

- No check ran live in this run. The passes recorded here are lane and bundle runs of 2026-10-10, 2026-11-25 and
  2026-11-26, each named on its verify. Their proof logs are on SteveDesktop, and this run did not read them. It read
  each result from the ledger run and the bundle state file.
- `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME`: the DLL check read ArchBig's deployed DLL only, not ArchSmall's or the
  SteveDesktop games' DLLs.
- `WARMTIMER_HARDEN_SPARE_LIVE`: the line-842 reading is yesterday's (2026-11-26, over the tailnet). This run did not
  read SteveDesktop again.
- The `REFUSE_OWNER_DEFECT_CLOSE` acceptance test was not re-run. Its first note says that it failed on `fc26ae8b12`, and
  `close --help` still has no `--regression`.
