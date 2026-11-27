# Parked pipeline and machine tickets, read 2026-11-26

Item: `RIMMANDRAKE_UNPARK_PIPELINE_TICKETS_NO_HOME_HAS_FIVE_READY` (the Conductor's brief, with the owner's authority).

The set: each ticket on a `pipeline:` or `machine:` home that `list_home.py offer` lists as parked (a block or a dated
wait ahead), and each ticket of those homes whose newest note is a `REFUSED BY BUNDLE` refusal (`work_bundle.refusals`;
the lane leaves such a ticket out of an onboarding run). Not read, by the brief's rules: the items of kind owed
(`RIMMANDRAKE_SETTLE_LANE_LEFTOVERS_OF_NOV_19_SITTING`, `RIMMANDRAKE_STUDY_WHAT_ONE_WEEK_OF_MODS_TAUGHT_ON_NOV_TWENTY_NINE`,
`RIMMANDRAKE_ENACT_GPT_STREAMLINE_REVIEW_TRUST_NOT_SUSPICION`, `RIMMANDRAKE_EVAL_CRYSTALLIZE_SKILL_ONCE_AFTER_EDITS_SETTLE`).
No ticket of the set was live or in a live bundle, and none was filed on 2026-11-26.

"Full-list hold" below is the owner's hold on full-list work until the integration phase (standing_rulings.md §Mod
development runs on small lists). "Owner card" is the block `PARKED by owner card (old workflow, stop now, may be useful
after the replan)` of 2026-11-01.

| ticket | home | park reason | class | evidence |
|---|---|---|---|---|
| `BRIDGETOOLS_DLL_REBUILD_THREE_TOOLS_MISSING` | pipeline:bridge | block by the retired Relentless pipeline: deploy the DLL with the game down | DONE (closed) | both deployed `JawaBench.BridgeTools.dll` (ArchBig and ArchSmall, 2026-11-26) hold all four named tools, byte search |
| `EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS` | pipeline:bridge | full-list hold | STAYS PARKED | A1 is proven only inside the full-list C0-C5 overhead run |
| `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD` | pipeline:bridge | full-list hold | STAYS PARKED | waits on the full-list overhead test (MUST 17) |
| `HEALTH_METRICS_PROVE_EIGHT_WRITTEN_UNTESTED` | pipeline:bridge | full-list hold | STAYS PARKED | deploys only after the full-list overhead test |
| `OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME` | pipeline:bridge | full-list hold | STAYS PARKED | waits on the full-list overhead test |
| `RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP` | pipeline:bridge | integration phase | STAYS PARKED | the C0-C5 protocol is full-list work |
| `FLYERFRAMES_PROVE_JOINT_SESSION` | pipeline:bridge | wait to 2026-12-03: owner act 1 | STAYS PARKED | only the joint flight session is left, his act 1 |
| `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD` | pipeline:bridge | bundle refusal: criteria at L4 | STAYS PARKED | A1, A2 pass at L2; the L4 level was set by FOUNDRY, a retired seat. Conductor call: rescope A1, A2 to L2 (a looser bar, his act) |
| `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` | pipeline:bridge | bundle refusal: L4, full list | STAYS PARKED | A1, A2 text names the full list; they pass at L2 on 30 mods |
| `BRIDGE_TPS_CAPTURE_FIXES_1` | pipeline:bridge | bundle refusal: C3 names the full list | STAYS PARKED | C3 second half is full-list. Conductor call: split off the small-list half (a bar change) |
| `BRIDGE_TPS_REVIEW2_FIXES_1` | pipeline:bridge | bundle refusal: C4 full list | STAYS PARKED | C4 is the full-list overhead measure |
| `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL` | pipeline:bridge | bundle refusal: A2 full list | STAYS PARKED | A2 is GREEN-FULL (>=300 mods) |
| `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP` | pipeline:bridge | bundle refusal: A10 stages a raid | STAYS PARKED | raid tests are paused (CLAUDE.md §A live test declares its kind) |
| `THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER` | pipeline:bridge | bundle refusal: A2 no fixture, A5 raid | STAYS PARKED | A2 needs a two-pack pawn that no small list holds; A5 stages a raid |
| `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW` | pipeline:operations | wait to 2026-11-28 on a live run | UNPARK (unwait) | the run ended; `RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL` is done |
| `OPS_STEVE_SEATS_RESTORE_QTWK_RGFZ` | pipeline:operations | bundle refusal: no defect to guard | NOT WORTH THE TOUCH (dropped) | each ring was a true SteveDesktop outage that self-healed; a new ring reopens the id |
| `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME` | pipeline:operations | full-list hold | STAYS PARKED | records every full-list session |
| `SEAT_MEMORY_PROVE_HARNESS_SLICE_OOM_KILLS` | pipeline:operations | owner card | NOT WORTH THE TOUCH (dropped) | memwatch.py:36 never toasts rm-harness.slice by design: a kill there is a selftest cap, reported KILLED |
| `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED` | pipeline:operations | owner card | STAYS PARKED | open C4 is a full-list A/B; C5 is a live check of a tier nobody arms now |
| `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO` | pipeline:operations | owner card | STAYS PARKED | only A3 (GREEN-FULL, full list) is open |
| `TELEMETRY_FAKE_DEPLOYS_EXCISE_NOT_REWRITE` | pipeline:operations | owner card | NOT WORTH THE TOUCH (dropped) | 159 old rows, source fixed in 0566579c8da3, no reader decides on them |
| `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES` | pipeline:operations | owner card | HIS PARK, STILL USEFUL | see the list below |
| `SELFTEST_CLOCK_BUILD_INJECTED_TIME` | pipeline:test-lane | owner card | STALE (dropped) | replaced by 4b7ba4ce90: a clock read keys the known result to its UTC day, it no longer refuses |
| `SELFTEST_SLOW_FOUR_SHRINK_BY_SPLIT` | pipeline:test-lane | owner card | STALE (dropped) | the four are mod selftests; the nightly checks FINISHED mods only (nightly_scope.py) |
| `SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB` | pipeline:test-lane | owner card | HIS PARK, STILL USEFUL | see the list below |
| `STEVE_FILLER_MONITOR_FAIL_FINDINGS` | pipeline:test-lane | wait to 2026-12-02: his SteveDesktop work switch | STAYS PARKED | `host_work_switch.py show` still reads the switch set |
| `SEAT_RESTART_FIX_TAKEN_REQUEST_LOST` | pipeline:conductor-tools | owner card | DONE (closed) | dispatcher.py:1827-1829 persists the pending restart before the request is consumed (5621583215) |
| `SEAT_GOODBYE_FIX_QUEUED_PROMPT_LOST` | pipeline:conductor-tools | owner card | STALE (dropped) | his rulings: typing at goodbye is an acceptable risk (2026-10-29); no text stops the goodbye (2026-11-01) |
| `SEAT_GOODBYE_FIX_REPLACEMENT_DIED_UNREAD` | pipeline:conductor-tools | owner card | NOT WORTH THE TOUCH (dropped) | a Codex prediction; no failure in 25 days |
| `DOORBELL_DELAY_FIX_FRESH_WINDOW_WAITS` | pipeline:dispatcher | owner card | DONE (closed) | stall_after_s 60; seat_restart._fresh_owed resets idle_since at a restart (ae07aa74b1) |
| `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` | machine:Archmagi | block by the retired Relentless pipeline: wait for the daemon restart | DONE (closed) | artpipe status/heartbeat.json written 9:44 PM PST today, rm-artpiped active, no `D:\Luke\dev\_*` dir |
| `FOCUS_ENFORCE_HEADLESS_LAUNCH_ALLOWLIST` | machine:Archmagi | owner card | NOT WORTH THE TOUCH (dropped) | a title with no spec and no failure on record; focus_heal and game_focus refuse without opt-in |
| `FOCUS_HEAL_TAME_HANDS_OFF_HIS_WINDOWS` | machine:Archmagi | owner card | NOT WORTH THE TOUCH (dropped) | built (focus_heal.py:105, selftest_game_focus green); only a live proof was owed |
| `DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING` | machine:Archmagi | wait to 2026-12-10: his physical reseat | STAYS PARKED | a physical act at the desk |
| `QUOTA_LEFT_AT_RESET_MEASURE_PER_ACCOUNT` | machine:accounts | owner card | DONE (closed) | `./acct measures` records the percent left at each reset, per account, per week |
| `WARMTIMER_HARDEN_SPARE_LIVE` | machine:accounts | owner card | HIS PARK, STILL USEFUL | see the list below |
| `HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE` | machine:SteveDesktop | integration phase | STAYS PARKED | A6 is full-list. Conductor call: A1-A3 name small tiers (bridge, fw_gss_sitting, pyrelands), so the hold may be wider than its reason |
| `HEAP_READ_BISECT_ROWS_NAME_THE_RETAINERS` | machine:SteveDesktop | full-list hold | STAYS PARKED | reads the rows of the heap bisect above |
| `REBOOT_BREAKGLASS_VERIFY_1` | machine:SteveDesktop | needs a Windows reboot at a moment he names | STAYS PARKED | his phone over cellular, his card 2026-09-19; its work is on Archmagi, not SteveDesktop |
| `ROLE_HEADERS_RETIRE_ENABLED_PROSE` | pipeline:docs | owner card | NOT WORTH THE TOUCH (dropped) | done in substance: roles/operations.md:4 and conductor.md:7 say the schedule decides; the lint guards no live fault |
| `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP` | pipeline:docs | wait to 2026-12-02: the Conductor's call on step 3 | STAYS PARKED | step 3 is his 2026-11-03 hold; the run of 2026-11-26 recommends a drop |
| `CLOSE_SHA_REPAIR_EIGHT_ON_LEAP_DAY` | pipeline:ledger | owner card | NOT WORTH THE TOUCH (dropped) | no process reads those old shas; the close gate now refuses a bad sha |
| `RIMMANDRAKE_REFUSE_OWNER_DEFECT_CLOSE_WITHOUT_REGRESSION` | pipeline:ledger | his ruling 2026-11-12: store look defects until the ladder is regenerated | STAYS PARKED | Conductor call: that ruling is from before the Maturation Pipeline (suspect); the acceptance test fails today |
| `MOD_HUMAN_EXPLORATION_PASS_1` | pipeline:maturation | after the art wave (2026-09-12) | STALE (dropped) | replaced by the owner's walk stage of the Maturation Pipeline (his act 3) |
| `NORTH_STAR_WALK_AUTHORING_1` | pipeline:maturation | block by FOUNDRY, a retired seat: owner reacts to drafts | STALE (dropped) | a mod's bars now lock in its own folder at its Design Version |
| `PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE` | pipeline:maturation | parked by the owner's words, 2026-10-31 | STAYS PARKED | "Once my live playtesting is the actual bottleneck we will reconsider." |
| `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY` | pipeline:maturation | wait to 2026-11-30 | STAYS PARKED | the 2026-11-29 study answers it; the date is ahead |
| `RIMMANDRAKE_INGEST_HELD_LOOK_DEFECTS_WHEN_LADDER_REGENERATED` | pipeline:maturation | his ruling 2026-11-12 | STAYS PARKED | the same Conductor call as the ledger row above |
| `RIMMANDRAKE_KILL_LIVE_HOLDER_RESUME_AFTER_FIRST_SESSION` | pipeline:maturation | wait to 2026-12-03: his walk of ExplosiveKnockback | STAYS PARKED | his act 3 |
| `OWNER_CARDS_HARDEN_DECISION_RECEIPTS` | pipeline:owner-review | wait to 2026-12-04: a census window | STAYS PARKED | a real date ahead |
| `PHONE_SENDS_ENFORCE_STILL_HONOR_SYSTEM` | pipeline:owner-review | owner card | HIS PARK, STILL USEFUL | see the list below |
| `RIMMANDRAKE_STOP_SHARED_COPIES_OUTLIVING_THEIR_LENDER` | pipeline:helpers | wait to 2026-11-27 | UNPARK (unwait) | its 7-day reading ended 3:44 PM PST 2026-11-26, before the wait date |
| `COLDLOAD_PROVE_DEFLOADCACHE_HALF_INSTALLED` | pipeline:deploy-and-lists | integration phase | STAYS PARKED | full-list cold-load proof |

`OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW` was closed by the lane soon after its wait was lifted.

## Count by class

53 tickets read: DONE 5, STALE 5, NOT WORTH THE TOUCH 8, UNPARK 2, HIS PARK, STILL USEFUL 4, STAYS PARKED 29.

## HIS PARK, STILL USEFUL: the list for the Conductor

- `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES`
  - Repairs: an unbounded cursor set in the telemetry exporter, and a KeyError on a heartbeat with no `at`.
  - Evidence: `~/.local/state/rm-telemetry/export_state.json` holds 79,332 `ledger_seen` entries (1.5 MB) and
    rm-telemetry-export.timer rewrites it every 5 min; `telemetry/health.py:40` still reads `hb["at"]` directly.
- `SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB`
  - Repairs: def-content checks that read no defs today, because no usable `defs.sqlite` exists.
  - Evidence: run 2026-11-26: `selftest_ecosystem_pyramid_check.py` and `selftest_label_collision_check.py` read
    UNMEASURED ("no usable defs.sqlite at ...\DefDump"). The repair needs a DefDump capture from a game (needs game-up).
- `WARMTIMER_HARDEN_SPARE_LIVE`
  - Repairs: the daily warm of the live Claude login when no claude process runs (the "auto log out" he banned).
  - Evidence: on SteveDesktop, claude-account-warm.timer is enabled (system unit) and `~/.local/bin/claude-account`
    line 842 skips the live login only `if w == "live" and claude_pids()`. The fix lands in the claude-remote-control
    repo, from Archmagi.
- `PHONE_SENDS_ENFORCE_STILL_HONOR_SYSTEM`
  - Repairs: a phone image from `chat_review.py` can reach him with no pre-review record.
  - Evidence: no hook in `.claude/` or in the settings names SendUserFile (searched 2026-11-26).

The two that would repair the most: `WARMTIMER_HARDEN_SPARE_LIVE` (a banned logout of the live login) and
`SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB` (def checks that today read nothing).

## Conductor calls that would free work (no owner act is needed for any of them)

- `BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD`: rescope A1 and A2 from L4 to L2 (they pass at L2), then close. A looser
  bar, so it is the Conductor's act.
- `BRIDGE_TPS_CAPTURE_FIXES_1`: split the small-list half of C3 off from its full-list half. A bar change.
- `RIMMANDRAKE_REFUSE_OWNER_DEFECT_CLOSE_WITHOUT_REGRESSION` and `RIMMANDRAKE_INGEST_HELD_LOOK_DEFECTS_WHEN_LADDER_REGENERATED`:
  say whether his 2026-11-12 ruling (store look defects until the validation ladder is regenerated) still stands.
- `HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE`: A1-A3 run on small tiers; only A6 needs the full list.
- `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP`: drop step 3 (recommended by its run of 2026-11-26).

## Ready old tickets per home after these acts

Read from `list_home.py offer` at about 10:05 PM PST 2026-11-26, then less the tickets that a bundle refused (the lane
leaves those out):

| home | offered | offered, less bundle refusals | still parked |
|---|---|---|---|
| pipeline:bridge | 7 | 0 | 6 |
| pipeline:operations | 3 | 3 | 4 |
| pipeline:helpers | 1 | 1 | 0 |
| pipeline:owner-review | 1 | 1 | 2 |
| pipeline:conductor-tools | 0 | 0 | 2 |
| pipeline:docs | 0 | 0 | 3 |
| pipeline:ledger | 0 | 0 | 1 |
| pipeline:maturation | 0 | 0 | 4 |
| pipeline:test-lane | 0 | 0 | 2 |
| pipeline:deploy-and-lists | 0 | 0 | 1 |
| machine:Archmagi | 0 | 0 | 1 |
| machine:accounts | 0 | 0 | 1 |
| machine:SteveDesktop | 0 | 0 | 3 |

(The "still parked" column also holds the kind-owed items that this run did not read.)

No `pipeline:` or `machine:` home has 5 ready old tickets after these acts. The reason is in the rows above. Of the 29
tickets that stay parked, 15 wait for the full mod list or the integration phase. 6 wait for one of his acts or a
physical act at the desk. 6 wait for a real date ahead, his ruling or a Conductor call (one of them an L4 level). 2 stage a
raid while raid tests are paused.
pipeline:bridge, the largest home, has 7 offered tickets, and a bundle refused every one of them for full-list work,
the raid pause or an L4 level. The Conductor calls above would free at most two bridge tickets. So no home reaches 5
until he opens the integration phase.
