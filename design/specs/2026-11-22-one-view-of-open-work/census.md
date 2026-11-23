# Census: where open work, status and his needs live, and what dropped (2026-11-16 to 2026-11-22)

Item: `RIMMANDRAKE_CENSUS_WHERE_OPEN_THINGS_LIVE_SEVEN_LISTS_STILL_DROP`. Written 2026-11-22, measured 6:53 PM to 7:10 PM
PST. His words (ledger, 2026-11-23T02:52Z): *"There is something odd happening. We have tickets, we have the Mods
themselves tracking their own growth. We have Conductor's handoffs tracking items. We have the Fleet Now and Maturation
Pipeline that have their own notes for me to consider... and yet things are getting dropped. We need a way to
consolidate all of this "what's going on, what's needed, what's next" etc. for the human especially."*

This page changes nothing. It acts on no owed item. The proposal is `proposal.md` beside this page.

**How it was measured.** One fold of every ledger shard (`infrastructure/state/ledger/events/*.jsonl`: 61,240 events
over 8,384 items) gives each item's state, kind, parent and notes. Then: `cli.py queue CONDUCTOR --owed --all`;
`owner_queue.py` and `owner_queue.py --misrouted`; greps of the five pages in `D:\ClaudeWork\rimmandrake\conductor\`;
a scan of every `` `ID` — … NEXT: `` pointer in the 19 handoffs written since 2026-11-15; `owner_rulings.py --since
2026-11-15 --kind said`; and `git log`, file reads and `ls` for the evidence of each owed act. Every count below is
`[measured]` at that time unless it carries a `[guess ~N%]` tag.

## Part 1: the stores

"Derived" means a program builds the store from other stores and holds no fact of its own. "Own facts" means the store
holds facts that exist nowhere else, so a reader who skips it loses them.

### Stores that hold open work, status or a need on him today (24)

| # | store | where | writer | reader | derived or own facts | is he meant to read it? | measured state |
|---|---|---|---|---|---|---|---|
| 1 | rimflow ledger: items | `infrastructure/state/ledger/events/*.jsonl` | `rimflow` (program), called by every model and program | every seat, every page | own facts (the store of record) | no, only through pages | 8,384 items; 1,597 not closed (open 769, built 612, blocked 144, waiting 37, doing 35) |
| 2 | the Conductor's owed items | ledger items of kind `owed`; `cli.py queue CONDUCTOR --owed` | the Conductor (model), by `rimflow file --kind owed` | the Conductor, at the start of a turn | own facts (part of the ledger) | no; nothing shows it to him | 48 open (44 actionable, 4 waiting); 38 marked LATE; oldest 6 days. 190 filed and 142 closed since 11-15; median close 2.1 h, so the open 48 are the tail |
| 3 | item prose | `infrastructure/state/items/<ID>.md` | models | seats via `rimflow show` | own facts | no | not counted |
| 4 | Conductor handoffs | `infrastructure/state/handoffs/` | the Conductor (model), `handoff.py` | the next Conductor window (`handoff.py --wake`) | own facts (judgement) plus pointers to ledger ids | no | 19 handoffs since 11-15 with 243 pointers on 168 ids; 42 of those ids are not done; the newest BENCH handoff is 2026-11-21 00:50Z, two days old |
| 5 | carry items | owed items such as `RIMMANDRAKE_CARRY_SUNDAY_SITTING_STATE_ACROSS_THE_WINDOW_RESTART` | the Conductor (model) | the next Conductor window | own facts (a sitting's state in one title of 1,900 characters) | no | 1 open; it replaces the handoff for today's sitting |
| 6 | Conductor log | `D:\ClaudeWork\rimmandrake\conductor\log.md` | the Conductor (model) and `run_end_wake` (program: "DETACHED RUN ENDED" lines) | the Conductor (`tail -n 40`) | own facts (quick-check reports) plus copies of run results | no | 2.3 MB, 8,383+ lines |
| 7 | situation briefs | `D:\ClaudeWork\rimmandrake\conductor\situation_<date>_<hhmm>.md` | the Conductor (model) | him, opened in Typora | own facts | yes, at each wake (`conductor.md` §Start of turn) | 6 in all; the newest is 2026-11-19 03:15. The practice stopped three days ago |
| 8 | FLEET_NOW (`RELENTLESS_NOW.md`, `FLEET_NOW.html`) | conductor folder | `running_now.py` + `fleet_mods.py` + `owner_queue.py`, `rm-running.timer` 1 min; `fleet_now.py` | him (a standing tab) | derived (ledger, run stores, machine readings) | yes | "NEEDS YOU, 4" at 6:53 PM; it read 10 earlier today when 4 were his |
| 9 | STATUS_BOARD | `conductor\STATUS_BOARD.html` | `status_board.py`, called by `running_now.py` | nobody; called dead on 11-19 | derived | no (retired on 11-19, *"Not Relentless, FLEET_NOW"*) | still written: 18:50 PST today, "Needs you (4)" |
| 10 | MATURATION_NOW (`.html`, `.md`, `MATURATION_NOW_phone\*.png`) | conductor folder | `maturation_now.py`, at each Dispatch tick | him (a standing tab, the phone), the Conductor | derived (concept folders, Dispatch `reading.json`, ledger) | yes | "Needs Mandrake (2)", "Needs Conductor (7)", "Pipeline now (20)". It read 82 under Needs Conductor at 11:55 AM |
| 11 | Dispatch reading | `maturation_dispatch.py` `reading.json` (`needs_conductor`, `hand_acts`) | program | `maturation_now.py`, the Conductor | derived | no | read through store 10 |
| 12 | Maturation hand acts | `maturation_hands.py list` | program (records each hand act of the Conductor) | the Conductor; alarm `MATURATION_HAND_ACT` | own facts | no | 13 open, 11 overdue, oldest 49 h; alarm open since 2026-11-22T02:14Z |
| 13 | the mod's own folder | `design/concepts/<Mod>/version/` (`VERSION.json`, `bars.md`, `gaps_sorted.md`, `polish.md`, `next_version/`, `stage_record.json`) and `stage.json`, the mod journal | the Designer, judges and drivers (models); `designer_stage.py`, `maturation.py` (programs) | the pipeline; him through store 10 | own facts (bars, gaps, next-version lists) | only through MATURATION_NOW | 13 mods have a `version/` folder; 6 have a `next_version/` folder. No `validation_holding` path exists under `design/concepts` (looked: `find … -path '*validation_holding*'` returned `[]`) |
| 14 | Designer turns | `designer_stage.py turns` | program | `owner_queue.py` | derived | through store 8 | 0 turns wait on him |
| 15 | owner queue rule | `owner_queue.py` (`is_his`, `--misrouted`, the "answered" bucket) and `infrastructure/state/owner_questions.json` | program; the questions file by models | stores 8 and 9 | derived; the questions file holds own text | through store 8 | 4 "truly his"; 9 "answered, the next move is ours" that no page or seat queue names as anyone's next act |
| 16 | showings | `D:\ClaudeWork\rimmandrake\showings\<ITEM>\` | helpers (models) | the Conductor, before a look | own facts (staged pictures, verdicts) | through the Conductor | 36 folders; no file named `READY*` in any of them |
| 17 | delegated digest | `Transient/delegated_digest_<date>.md` in the Conductor's clone only (untracked) | `rimflow/delegated_digest.py` (program) | him, delivered by the Conductor | derived (ledger, judge files, commits, art acts) | yes, daily | 11-20: 2,743 lines; 11-21: 690; 11-22: 270 |
| 18 | ops watch | `D:\ClaudeWork\rimmandrake\ops_watch\` (`digest.md`, `alarms.json`, `incidents.json`, `flags.json`) | `ops_watch.py` (program, 15 min) | Operations, the Conductor | derived readings plus own incident plans (model text) | no | 6 alarms open, 1 pending, 21 flags. `PLAN_DISTRESS` open since 2026-11-13: the priority list is spent, 203 h old |
| 19 | Operations owner-only proposals | `ops_watch\owner\OP-*.md` | Operations (model) | the Conductor | own facts | no | not counted |
| 20 | Conductor goals | `infrastructure/state/CONDUCTOR_GOALS.md` | the Conductor (model) | the Producer | own facts | no | last change 2026-11-15. His plan of 2026-11-22 (one week on mods to 11-29) is only in an OWNER ledger note |
| 21 | Producer priority list | `infrastructure/state/priority_list.json` | the Producer (model) | Dispatch, `ops_watch` | own facts | no | last change 2026-11-14; spent (alarm in row 18) |
| 22 | cards | `D:\ClaudeWork\rimmandrake\cards\cards.jsonl` | `card_capture.py` (program), on his answer | ledger stamps | own facts | no | 161 records, all answered; 79 answered since 11-15. A card that was asked and not answered is in no store |
| 23 | the Conductor's auto-memory | `~/.claude/projects/-home-mandrake-rm-bench/memory/` | the Conductor (model) | the Conductor | own facts | no | 70 files; `MEMORY.md` 86 lines, changed 2026-11-22 5:20 PM |
| 24 | Lodestar tickets for this project | `python3 ~/dev/Lodestar/bin/ticket.py list --project rimmaster` | models in other sessions | Lodestar orders; no RimMandrake page | own facts | through Lodestar only | 3 open; 2 owned by him (`RIMFLOW_SAID_FLAGS_RETIRE_GATE` proposed, `RIM-2 (RimFlow: refresh the stated blocks so every one is true)` open) |

Also read for the census, but not a store of open work: `CODEBASE_NOW` (code health), the canon findings
(`canon_sweep\findings.md`), `design/RimMandrake/innovations.md` (last change 2026-11-19).

### Retired stores still on disk (6)

Nobody writes these and nobody reads them. Each still holds text that reads like open work to a cold reader.
`infrastructure/state/OWNER_DECISIONS.md` (2026-08-26), `BENCH_HANDOFF.md` (2026-09-19), `LIVE.md` (2026-08-26),
`board/` (2026-09-10, a tombstone), `queue/*.md` (17 files, 2026-10-02), and `ARTISAN_NOW.md` and `WHITTLE_NOW.md` in
the conductor folder (2026-11-13).

### What the stores show together

- **The owner is meant to read five of the 24 stores** (FLEET_NOW, MATURATION_NOW, the situation brief, the delegated
  digest and, by accident, STATUS_BOARD). Each of the five is built by a different writer, from a different subset of
  the stores.
- **Two pages answer "what needs him" with two rules.** At 6:53 PM FLEET_NOW said 4 (drawbridges, flyer frames, liquid
  pump redraw, the Pyrelands walk picks). MATURATION_NOW said 2 (the Pyrelands walk picks, and a Gimme Some Slack
  question that is addressed "to the Conductor"). The two lists share one row.
- **No page shows the Conductor's own owed queue.** The 48 owed items live in one ledger kind and are read only by the
  Conductor window, at the start of its turn. When the window does not read them, nobody does.
- **Three stores hold facts that no program reads back:** the handoffs, the carry item and the Conductor log. A pointer
  that is in a handoff and not in an owed item lives only in model prose.

## Part 2: the drops of the last seven days

A drop is something asked, promised or needed that then went unacted for over a day, or reached him late, wrong or
never.

### 2a. The 48 owed items on the Conductor's queue

Classes: **DONE** = the act happened (the evidence is named) and the item was not closed. **STALE** = a later ruling
or act made the item moot. **STILL OWED** = the act did not happen. A STILL OWED row is a **drop** when it was ripe
(its trigger had come) for over a day.

| age | item | class | one line of evidence |
|---|---|---|---|
| 6d | `RIMMANDRAKE_RELEASE_CONTAGION_JUDGE_ONE_LOOK_HIS_WORD_GIVEN` | STILL OWED, a valid wait | waits on his six-mod hold of 2026-11-16 (until 11-23) |
| 5d | `RIMMANDRAKE_COUNT_STEVE_FAULTS_AFTER_VOLTAGE_RAISE_TO_CEILING` | DONE | the 72 h count is noted 2026-11-20T19:40Z. The re-scoped lane count (48 h due 11-22 12:07 PM PST) has no reading and no item of its own |
| 5d | `RIMMANDRAKE_FIX_FILED_PIPELINE_TICKETS_AFTER_WEDNESDAY_RESET` | STILL OWED, **drop** | its wait expired 2026-11-21T10:00Z with no event since; part 3 (Test Pilot against the Fable Rescuer) has no record |
| 5d | `RIMMANDRAKE_BUILD_CODEX_BUILDER_LANE_WHILE_CLAUDE_RUNS_DRY` | STILL OWED, **drop** | the pilot outcome was read 11-19 (2 of 16 tickets reached LAND); no decision since |
| 4d | `RIMMANDRAKE_VERIFY_BIOME_CHOICES_BEFORE_OLD_FILES_GO` | STILL OWED, **drop** | all five `RECHECK_*_CHOICES` items read done by 2026-11-19T04:45Z; no record that he read the choices pages |
| 4d | `RIMMANDRAKE_GROUP_BIOME_QUESTIONS_BY_THEME_FOR_ONE_SITTING` | DONE | `conductor\biome_open_after_picks_20261120.md` opens "after your card picks of 2026-11-20" |
| 3d | `RIMMANDRAKE_WORK_EIGHTY_OWNER_TICKETS_AFTER_GATES_OPEN` | STILL OWED, **drop** | the 11-19 run proposed 103 commands over 110 tickets and ran none; 80 of the 110 are still open; its wait expired 11-20 08:00Z |
| 3d | `RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO` | STILL OWED, **drop** | its wait expired 2026-11-21T08:00Z; `RIMMANDRAKE_PRICE_CEILING_AND_DESIGNER_TOKENS_FOR_PINNED_MODEL` still open |
| 3d | `RIMMANDRAKE_LAUNCH_ELEVEN_RARE_FAILURE_LANES_BRIEFS_ARE_READY` | STALE | its own note (11-20 02:34Z): the touch-cost ruling replaced the blanket launch; the slices launched on 11-20 |
| 3d | `RIMMANDRAKE_READ_CLAUDE_DRAIN_RESULT_REREAD_IT_COLD` | STALE | the CLAUDE.md that it would reread was rewritten again by the crystallize pass of 2026-11-21 |
| 3d | `RIMMANDRAKE_DEFINE_STAMP_ONLY_RELAY_LINE_COLD_READER_STUCK` | DONE | `CLAUDE.md` now says "A game-state relay is stamp-only: `./game` writes the ledger event and messages no window." |
| 3d | `RIMMANDRAKE_REPORT_CLEAN_SHARE_HISTORY_TREEMAP_WAS_ALL_GREEN` | STILL OWED, **drop** | the census exists (`conductor\clean_share_history_20261119.md`, 11-19 3:58 PM); no log line or note says he was told |
| 3d | `RIMMANDRAKE_COLLECT_REWRITE_CONFLICTS_UNDEFINED_TERMS_ONE_LIST` | STILL OWED, **drop** | no list exists; `2026-11-21-crystallize-rule-files/results.md` still lists conflicts "for the Conductor" |
| 3d | `RIMMANDRAKE_REPORT_DAILY_FILED_COUNT_AFTER_FILING_GATE_STARTS` | STILL OWED, not yet due | its window ends 2026-11-23; filed with no wait, so it reads LATE before it is due |
| 3d | `RIMMANDRAKE_DOCUMENT_REVIEW_LOOPS_IN_CODEFIX_STRATEGIES` | DONE | `D:\Luke\dev\MandrakeWorkflows\codefix-strategies\` exists; MandrakeWorkflows commits `64a9fb3`, `0b1d646` (11-19) |
| 3d | `RIMMANDRAKE_LAUNCH_REMAINING_PLAIN_ENGLISH_BATCHES_ELEVEN_LEFT` | STILL OWED, **drop** | crystallize `results.md` §The plain-English batches: `standing_rulings.md` 11 of 70 sections done; five batch groups "not touched" |
| 3d | `RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING` | STILL OWED, **drop** | 22 of the 29 pointers of `BENCH_REBOOT_HANDOFF_202611200206.md` are still not done; no commit or log line cites this item |
| 3d | `RIMMANDRAKE_READ_REVIEW_METHOD_RUNS_THEN_LAUNCH_SCAN` | STILL OWED, **drop** | `RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET` open since 2026-11-20T02:03Z, never launched |
| 3d | `RIMMANDRAKE_LAUNCH_TICKET_JUDGING_SLICES_WHEN_PLAN_LANDS` | STILL OWED, **drop** | 6 slice items were filed; 4 of them wait past their 11-22 08:00Z date; the run-clone slice was never filed |
| 2d | `RIMMANDRAKE_CHECK_SCRATCH_QUEUE_SHRINKS_BEFORE_INCIDENT_CLOSES` | STILL OWED, **drop** | incident `disk-20261115210535` still open (recover by 11-23 15:40Z); alarm `SCRATCH_DIRTY_END` open |
| 2d | `RIMMANDRAKE_LAUNCH_RUN_CLONE_GROUP_AFTER_LIVE_RUNS_END` | STILL OWED, **drop** | `RIMMANDRAKE_JUDGE_RUN_CLONE_DEPLOY_TICKETS_WORTH_THE_TOUCH` was never filed (no ledger record) |
| 2d | `RIMMANDRAKE_ROUTE_SLACK_VISIT_TWO_FAILURES_READ_LATE_RUNS` | STILL OWED, **drop** | part 1 done by the pipeline (note 11-20 09:24Z); parts 2 to 5 have no record |
| 2d | `RIMMANDRAKE_ASSIGN_LEFTOVER_CONTEXT_CHANGES_NEITHER_WORKER_HAD` | STILL OWED, **drop** | no launch; no commit cites it |
| 2d | `RIMMANDRAKE_RERUN_FAULT_WINDOW_VERDICTS_ON_CLEAN_BOOT` | STILL OWED, **drop** | no suspect tag and no rerun; no commit cites it |
| 2d | `RIMMANDRAKE_READ_STEVE_RESUME_REPORT_CAN_FILL_RAISE_NOISE` | STILL OWED, **drop** | ColdStorage `stage.json` still at stage 0 (init 11-20); no park record; no reading of the re-run chains |
| 2d | `RIMMANDRAKE_ADD_FRIDGE_ART_TO_ELECTRICAL_RESKIN_HOME` | STILL OWED, **drop** | parent done 2026-11-21T00:40Z; no Machine Looks concept folder exists, so the fridge scope was not added |
| 2d | `RIMMANDRAKE_LAUNCH_CODEX_REVIEWS_OF_MOD_CODE_AND_ART` | STILL OWED, **drop** | its block (the Codex sign-in) closed today (`RIMMANDRAKE_RESTORE_CODEX_LOGIN_REVOKED_ON_BOTH_SIDES` done 02:35Z); FlowWorks and art parts not launched |
| 2d | `RIMMANDRAKE_REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE` | STILL OWED, deferred | waits for Machine Looks' art work (parent open); filed with no wait |
| 2d | `RIMMANDRAKE_WORK_NIGHT_POINTERS_OF_NOV_TWENTY_SWITCH_HANDOFF` | STILL OWED, **drop** | Machine Looks not admitted (`RIMMANDRAKE_ADMIT_MACHINE_LOOKS_MOD_WITH_FRIDGE_AND_BATTERY` open); no commit or log line cites this item |
| 2d | `RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION` | STILL OWED, **drop** | batch one says "delete the promise scanner"; `src/RimMandrake/rimflow/promise_scan.py` still exists; no commit names the batch |
| 38h | `RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX` | STILL OWED, **drop** | FlowWorks sweep 11-22 kept it; not sent to the Designer |
| 36h | `RIMMANDRAKE_CARD_STEVE_AUDIO_DRIVER_CURE_FIVE_OPTIONS_FOR_HIM` | DONE | answered 11-21 11:12 AM PST (note); `RIMMANDRAKE_DISABLE_STEVE_SONIC_STUDIO_DRIVER_SOUND_IS_UNUSED` done |
| 36h | `RIMMANDRAKE_DECIDE_TWELVE_RULE_CONFLICTS_THE_COMPRESSION_LISTED` | STILL OWED, **drop** | the length ceiling is deferred to ~12-05 by him (note 11-21); the twelve conflicts are not decided |
| 25h | `RIMMANDRAKE_WRITE_FOLLOWUP_CARD_ANSWERS_INTO_CONVERSION_LIST` | STILL OWED, **drop** | `conversion_list.md` line 485 still says "rulings A11 (open question); rulings A12 (open question)"; they were RULED 2026-11-22T01:34Z. The file is false now |
| 20h | `RIMMANDRAKE_READ_SLACK_WALK_BRIEF_ARRIVAL_TWO_BEFORE_STAGING_HIS_WALK` | DONE | his Gimme Some Slack walk ran today and is over (carry note 02:15Z) |
| 15h | `RIMMANDRAKE_READ_FLOWWORKS_WALK_BRIEF_ARRIVAL_TWO_BEFORE_STAGING_HIS_WALK` | DONE | FlowWorks walk two ran; `RIMMANDRAKE_ROUTE_FLOWWORKS_WALK_TWO_FINDINGS_BACK_ELEVEN_FILED` ended 00:12Z |
| 3h | `RIMMANDRAKE_BRING_HIM_THE_CLEAN_HOUSE_ADVICE_AND_BOTH_CODEX_STUDIES` | STILL OWED, part done | he ruled on the clean-house plan by card (OWNER note 02:00Z); the GPT-door and art-pipeline pages have no delivery record |
| 3h | `RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST` | STILL OWED | part 1 answered today; parts 2 and 4 are his |
| 3h | `RIMMANDRAKE_CARRY_SUNDAY_SITTING_STATE_ACROSS_THE_WINDOW_RESTART` | STILL OWED | the live sitting's carry |
| 2h | `RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS_HEAVY_B_CHOSEN_TWO_PICKS_OPEN` | STILL OWED | doing; art installed (`05014cbca2`); the live look waits for ArchSmall |
| 1h | `RIMMANDRAKE_WEIGH_DROIDWORKS_SOON_SO_DROIDS_JOIN_EVERY_MOD_TEST` | STILL OWED | new |
| 54m | `RIMMANDRAKE_STUDY_WHAT_ONE_WEEK_OF_MODS_TAUGHT_ON_NOV_TWENTY_NINE` | STILL OWED, not yet due | dated 11-29; filed with no wait |
| 46m | `RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS` | STILL OWED | new |
| 23m | `RIMMANDRAKE_DEPLOY_THIN_OUTLINE_ULLAI_INSTALLED_BUT_NO_GAME_HAS_IT` | STILL OWED | new |
| 23m | `RIMMANDRAKE_TELL_HIM_STEVE_IDLE_CAUSE_AND_TEN_NEEDS_TRIAGE_RESULTS` | STILL OWED | new |
| 3d | `RIMMANDRAKE_CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED` | STILL OWED, **drop** | waits to 11-26 on "he paused it", but its own note (11-20 07:29Z) says he reopened it; `secrets\pushover.env` now exists |
| 3d | `RIMMANDRAKE_EVAL_CRYSTALLIZE_SKILL_ONCE_AFTER_EDITS_SETTLE` | STILL OWED, a valid wait | waits on his word (to 11-26) |
| 30h | `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES` | STILL OWED, a valid wait | waits to 11-28 for the open rows |

**Totals:** 7 DONE, 2 STALE, 39 STILL OWED. Of the 39: 25 are drops (ripe over a day, no act), 6 are valid waits or not
yet due, and 8 are under four hours old. So 9 of the 48 (19%) can close now on the evidence above, and 25 are real
drops.

### 2b. Drops outside the owed queue

- **Waits that expire into silence.** 21 of the 37 waiting items in the ledger are past their `until` date with no
  later event (16 tasks, 5 owed). The oldest expired on 2026-11-20 08:00Z. Nothing alarms on an expired wait.
- **Handoff pointers that no owed item carries.** Of the 42 not-done ids that handoffs since 11-15 point at, 24 have
  no owed item that names them. 13 of those 24 are carried only by an owed item that names the handoff file
  (`SETTLE_LANE_LEFTOVERS…`, `WORK_NIGHT_POINTERS…`), and both of those owed items are drops above. The other 11 have
  no carrier at all, last touched 2 to 7 days ago (for example `RIMMANDRAKE_ADMIT_CONTAGION_AS_NEXT_BIOME`,
  `RIMMANDRAKE_NAME_STAGE_CEILING_DANGER_OR_REMOVE_THE_LIMIT`, `TEN_FINDINGS_UNCLAIMED`, not in the ledger). Whether
  each of the 11 is a real drop or sits on a seat queue that will offer it: `[guess ~60%]` real.
- **The NEEDS YOU list was wrong for him.** Fleet Now read 10 today when 4 were his (triage `4157ca8c04`). Of the 6
  wrong rows, 5 were the Conductor's to act on (Assailant war-lab reads, Rot blastpod floor, Sekkulaath clauses,
  thrixweave price check, Contagion limb costs, held) and 1 was already done (the Codex sign-in). Three of the five
  (`RIMMANDRAKE_DECIDE_ROT_BLASTPOD_GROWS_ONLY_ABOVE_FIFTY_DEGREES`, `THRIXWEAVE_RESELL_BUILD_DEARLY_SOLD`,
  `RIMMANDRAKE_DESIGN_CONTAGION_LIMB_COSTS_FIVE_LIMBS_WAIT`) were in the 11-19 set of 110 whose re-route commands
  were proposed and never run (`WORK_EIGHTY` above). That is one drop seen twice: once as an owed item, once as a
  wrong row on his page.
- **The Needs Conductor list was noise for him.** MATURATION_NOW read 82 under Needs Conductor at 11:55 AM, most of
  them records of runs that had ended up to six days before (`design/specs/2026-11-22-needs-conductor-list/`).
- **"Answered, the next move is ours" belongs to nobody.** `owner_queue.py` lists 9 items he answered whose next move
  is ours. They are still routed `for=OWNER`, so no seat queue offers them, and no page names who acts.
- **A ruled plan that the goal store never got.** His card of 2026-11-22 (one week on mods to 11-29) is in an OWNER
  ledger note. `CONDUCTOR_GOALS.md` last changed 2026-11-15. The Producer's `priority_list.json` is from 2026-11-14,
  and the `PLAN_DISTRESS` alarm has been open since 2026-11-13 (9 days).
- **A practice that stopped.** The situation brief that `conductor.md` asks for at each wake was last written
  2026-11-19 03:15.
- **A retirement that did not happen.** STATUS_BOARD was called dead on 2026-11-19 and is still written each run.
- **His own words that say something was missed or repeated** (`owner_rulings.py --since 2026-11-15 --kind said`):
  - 11-22 23:26Z: *"I feel like I keep asking for studies like this, and they do not come back to me."*
  - 11-22 19:54Z: *"MATURATION_NOW shows 82 items "need conductor" What is all that alert spam, and why is it in the
    status page?"*
  - 11-22 19:22Z: *"Why did I just have to re-login? It said the login expired. I thought we fixed that."*
  - 11-21 04:24Z: *"There are two live games. … You keep getting that wrong. … Please stop saying waiting for the
    live game."*
  - 11-17 18:51Z: *"Sounds like something that should be instructed to the mod builder in general, yes, from the
    get-go? I kinda thought we already had"*
  - 11-15 19:38Z: *"You are repeatedly asking me to rule on whether 0.1.0 is appropriate for a new mod."*

### 2c. Drops per hand-over

Each drop is counted once, at the hand-over where it fell.

| hand-over | what falls | drops | which |
|---|---|---|---|
| run → Conductor | a run ends with a result or a `LEFT OPEN:` note; the act that the result enables is not done | 10 | owed: ASSIGN_LEFTOVER, BUILD_CODEX, COLLECT_REWRITE, ENACT_GPT, FIX_FILED_PIPELINE, LAUNCH_TICKET_JUDGING, READ_REVIEW_METHOD, READ_STEVE_RESUME, WORK_EIGHTY; plus the 5 mis-routed NEEDS YOU rows, counted once with WORK_EIGHTY. Owner words: "studies … do not come back to me" (1) |
| Conductor → him | the Conductor owes him a word, a card or a page | 5 | owed: CARD_PHONE_ALERT, DECIDE_TWELVE, READY_PIPELINE_WRECKED, REPORT_CLEAN_SHARE, VERIFY_BIOME |
| page → him | a page shows him a need that is not his, or noise | 3 | NEEDS YOU 10 for 4; Needs Conductor 82 mostly history; two pages with two "his" lists (4 and 2, one shared) |
| window → window | a handoff or a "next window" line; the next window does not take it | 4 + 11 | owed: LAUNCH_RUN_CLONE, ROUTE_SLACK, SETTLE_LANE, WORK_NIGHT; plus 11 handoff pointers with no carrier (`[guess ~60%]` real) |
| store → store | a ruling or fact lands in one store and the store that acts on it does not change | 7 + 7 | owed: ADD_FRIDGE, CHECK_SCRATCH, DECIDE_MOAT, LAUNCH_CODEX_REVIEWS, LAUNCH_REMAINING_PLAIN, RERUN_FAULT, WRITE_FOLLOWUP; plus the goals store (11-22 plan), the 9 "answered" items, the STATUS_BOARD retirement, and the owner-reported repeats (two games; offline model; 0.1.0; login) |
| wait → nobody | a wait expires and nothing raises it | 21 | 21 of 37 waits past their date (5 of them owed items, also counted above) |
| him → ledger | something he said is not recorded | UNMEASURED | this census did not compare transcripts with ledger events; the instrument for it does not exist here |

## Minor things seen (no ticket)

- `cli.py queue CONDUCTOR --owed` marks 38 rows LATE; the brief counted 44 LATE, which is the "actionable" count.
- 762 distinct "left work no remote had … restore it if the work is still wanted" notes since 11-15, and 80 bundles
  on disk. Whether any bundle holds work that never landed: UNMEASURED.
- Items filed for a future date (`STUDY_WHAT_ONE_WEEK…`, `REPORT_DAILY_FILED_COUNT…`) read LATE before they are due,
  because they were filed with no wait.
