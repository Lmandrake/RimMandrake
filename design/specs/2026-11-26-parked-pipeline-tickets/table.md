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

## HIS PARK, STILL USEFUL: the list for the Conductor

- `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES`
  - Repairs: an unbounded cursor set in the telemetry exporter, and a KeyError on a heartbeat with no `at`.
  - Evidence: `~/.local/state/rm-telemetry/export_state.json` holds 79,332 `ledger_seen` entries (1.5 MB) and
    rm-telemetry-export.timer rewrites it every 5 min; `telemetry/health.py:40` still reads `hb["at"]` directly.
- `SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB`
  - Repairs: def-content checks that read no defs today, because no usable `defs.sqlite` exists.
  - Evidence: run 2026-11-26: `selftest_ecosystem_pyramid_check.py` and `selftest_label_collision_check.py` read
    UNMEASURED ("no usable defs.sqlite at ...\DefDump"). The repair needs a DefDump capture from a game (needs game-up).
