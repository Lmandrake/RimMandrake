# Evidence: the census of offline simulations (2026-11-26)

Page: `one_page.md` beside this file. Item: `RIMMANDRAKE_CENSUS_SIMULATIONS_ASK_AT_DESIGN_FIRE_HAS_ONE`.
Read on the clone of origin/main of 2026-11-26 6:21 PM PST. The fault window is 2026-11-12 to 2026-11-26.

## How the census looked

- **Simulations.** Every `src/RimMandrake/<Mod>/Source/Kernel/` and `Source/SelfTest/` (each `.csproj` read for the
  files that it compiles), every `src/RimMandrake/Utils/sim/` file, and a search of `rimflow/`, `Utils/`,
  `Utils/testq/` and `infrastructure/stevedesktop/` for the words of what such code does: simulated, fake clock,
  replay, sweep, regime, world rig, kernel, fuzz. Item and lesson titles with kernel, replay, twin and sim were also read.
- **Faults.** 2,657 items filed in the window (ledger shards, `file` events). Titles were matched per machine, then the
  item prose and its ledger events were read for a measured duration. Two studies of the same days carry most hours:
  `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and
  `design/specs/2026-11-26-stuck-items-study/one_page.md`.
- **Hours.** Wall hours that work stood still or ran wasted, as each source measured them. Hours of faults in one row
  are added, so a total is an upper bound where they overlap. A fault with no measured duration reads UNMEASURED.
- **The classes** follow the Conductor's reading in the brief (not the owner's words): a simulation pays for a state
  machine or physics with many cases and a slow live test; not for art, a def with no logic, or a thing one cheap live
  look decides; real code beats a copy.

## Mods

| mod | class | what exists, and what it covers | real code or copy |
|---|---|---|---|
| Pyrelands | HAS ONE | `pyre_burn_sim.py`: the whole-map burn (vanilla Fire, the weather decider, the burn line, fire clock, black rain, regrowth), checked by `validate_against_walk` against the two-week walk's per-cell burn grid. Six kernels (`Source/Kernel/RM_BurnKernel.cs`, `RM_FireEcoKernel.cs`, `RM_FireHawkKernel.cs`, `RM_FireHawkRewardsKernel.cs`, `RM_FoamPathKernel.cs`, `RM_FurnaceKernel.cs`) under `Source/SelfTest/Fuzz/` | burn model: a copy, its regrowth fitted to the walk saves; kernels: real code |
| Explosive Knockback | HAS ONE | `Source/SelfTest/KnockbackFuzz.cs`, `KnockbackSweep.cs`, `KnockbackMap.cs` (an enumerated map of lanes read by the bars' own checks) over `RM_KnockbackPlan.cs`, `RM_KnockbackMath.cs`, `RM_KnockbackVerdicts.cs`; `Source/SelfTest/LosReal/` links the game's Assembly-CSharp and asks the real `GenSight.LineOfSight`: 0 of 999,162 lines differ from the model's copy (`design/specs/2026-11-25-offline-real-game-code-probe/README.md`) | real code; real game code for sight lines |
| FlowWorks | HAS ONE | `Source/RM_FlowKernel.cs`, `Source/Machinery/RM_LiquidNetKernel.cs`; `Source/SelfTest/FlowKernelFuzz.cs`, `SequenceFuzz.cs` (random action sequences over cells, bodies and tanks, with a per-fluid ledger; `design/RimMandrake/flowworks_offline_kernel_B.md`) | real code for every number; the composition (which cell touches which body) is the test's own model |
| Gimme Some Slack | HAS ONE | `Source/SelfTest/LabWorld.cs` lays a dumped live colony (`worlddump`) with the production cord builder; `GssFuzz.cs`, `LiveEndSweepChecks.cs`, `DeterminismChecks.cs` | real code. Known gap: a replay is as wide as its dump (lesson `20261117T162555Z-BENCH-gimme-some-slack-offline-replay-live.md`: three live failures on regimes the dump did not carry) |
| Wrecked Machines | HAS ONE | `Source/Kernel/RM_WreckedMachinesKernel.cs` and `_Shared/SalvageRule/RM_SalvageRuleKernel.cs` under `WreckedFuzz.cs`; `Source/tests/salvage_exec/FakeEngine.cs` with `Oracle.cs`; `prove_alloy_forge_offline.py` applies our shipped patches to the real VFE Factory defs | kernels: real code; the forge cost rule in `prove_alloy_forge_offline.py` is a mirror (a copy) of one C# rule |
| Cauldron (held) | HAS ONE | six kernels (`RM_AcidAirKernel`, `RM_RhossakKernel`, `RM_VentGasKernel`, `RM_VentKernel`, `RM_VexxissKernel`, `RM_YieldKernel`) under `CauldronFuzz.cs` | real code |
| Contagion (held) | HAS ONE | six kernels (`RM_CoalescenceKernel`, `RM_DraftprintKernel`, `RM_SkyKernel`, `RM_TellRenderKernel`, `RM_TouchedKernel`, `RM_ZhoolHazeKernel`) under `ContagionFuzz.cs` | real code |
| FeverWood (held) | HAS ONE | five kernels (`RM_BroodKernel`, `RM_HiveLayoutKernel`, `RM_LureKernel`, `RM_PoolKernel`, `RM_TankKernel`) under `FeverWoodFuzz.cs` | real code |
| GelatinousSlime (held) | HAS ONE | `RM_SlimeLadder.cs`, `RM_SlimeWorld.cs`, `RM_TitanKernel.cs` under `GelatinousSlimeFuzz.cs` | real code |
| Graffiti (held) | HAS ONE | `RM_GraffitiKernel.cs` under `GraffitiFuzz.cs`; `art_source/gallery_sim.py` shows every baked mark on real wall tiles at play zoom (an art view, not logic) | real code |
| LeaningScrub (held) | HAS ONE | twelve kernels (blaze, coat, forms, four forms, glide, injection, island, lean, pyre, ripple, smother, stall hunt) under `LeaningScrubFuzz.cs`, `LeaningScrubFuzz2.cs`, `LeaningScrubFourFormsCheck.cs` | real code |
| Stillsand (held) | HAS ONE | six kernels (`RM_DuneTrackKernel`, `RM_GaleKernel`, `RM_HorizonMath`, `RM_LedgerKernel`, `RM_LeviathanKernel`, `RM_SunKernel`) under `Source/SelfTest/Fuzz/StillsandFuzz.cs` | real code |
| ColdStorage (admitted, waits for its readiness list) | HAS ONE | `Source/Kernel/ColdStorageKernel.cs` under `Source/SelfTest/` | real code |
| MachineLooks (admitted at intake) | WOULD NOT | art reskins of vanilla machines; no mod folder yet (`design/concepts/MachineLooks/admission_proposal.md`). A cheap live look decides art | no logic |
| PyrelandsMechanics, the Deep Desert Tribes (held; faction work waits for his word) | WOULD BENEFIT, a guess | the fire rite, the visit and the fruit defence are event state machines (`design/concepts/PyrelandsMechanics/README.md`). No fault in the window, because the mod sleeps. Its design answers the question when faction work starts | none exists |

**The gap that every HAS ONE mod shares.** A kernel fuzz compiles only the kernel. It never runs the ThoughtWorker,
patch or building that calls the kernel. Measured on 2026-11-07: 0 of 31 planted faults in callers caught, 21 of 21 in
kernels (lesson `20261108T013344Z-BENCH-kernel-fuzz-cannot-see-callers.md`). The probe of 2026-11-25 runs real game
geometry, seeded `Rand` and the real sight line offline, but not `ThingMaker`, loaded defs or `Find.*`
(`design/specs/2026-11-25-offline-real-game-code-probe/README.md`). The builder's offline-model block already asks for
this form (`src/RimMandrake/rimflow/roles/builder.md`, `offline-model`). The census did not class each mod's live faults
by whether a caller simulation would have caught them: UNMEASURED.

## Pipeline state machines

| machine | class | what exists | real code or copy |
|---|---|---|---|
| The account plan | HAS ONE | `src/RimMandrake/Utils/account_plan_sweep.py`: the real `account_plan.tick` every 5 minutes through a simulated week, over 378 regimes in 63 regions; stand-ins only for the meter's poll, the switcher, the live runs, ssh, the phone and the ledger. On 2026-11-25 it found 5 reachable wrong-switch classes before they happened live, two of them in that night's regions (`design/specs/2026-11-25-account-plan-sweep/regime_map.md`). `account_plan_replay.py` decides again 4,095 recorded passes of 2026-11-10 to 2026-11-24 (`design/specs/2026-11-24-account-plan-one-file/replay.md`). `account_plan_mutants.py` plants faults | real code |
| The restart of the Conductor window | HAS ONE | `src/RimMandrake/rimflow/restart_world.py`: real child processes with session files, transcripts and doorbells; the real `dispatcher.tick`, `decide`, `execute` and `kill_pid` on production thresholds; a simulated clock. Read by `selftest_handoff_restart.py` and the `selftest_seat_restart*.py` family (simulated windows). Fault in the window that it did not model: a restart held silently over 2 h for a ledger line that another process wrote (2026-11-15, `RIMMANDRAKE_PUBLISH_HELD_RESTART_LEDGER_LINE_SILENT_TWO_HOURS`) | real code |
| The process as a whole | HAS ONE | six models in `src/RimMandrake/Utils/sim/`: `process_sim.py` (a discrete-event model of tickets, builders, Dispatcher, roles, owner attention and budgets, with `process_sim_params.json`), `loop_sim.py` (the single-prompt loop beside it), `fanout_sim.py` (every architecture on equal fan-out terms), `ctx_strategy_sim.py` (context strategies of a perpetual seat), `testing_investment_sim.py` (where more testing pays), `testpilot_sim.py` (the three-agent proposal). Each has a selftest. They compare architectures; they model the era of 2026-10, its builder seat included, not today's Maturation Pipeline | copies, with fitted parameters |
| The SteveDesktop test lane | WOULD BENEFIT | example selftests in `src/RimMandrake/Utils/testq/` (`selftest_lane_stop.py`, `selftest_ask_lane.py`, `selftest_brake_release*.py`, ...) and acceptance scripts in `design/specs/2026-11-23-stevedesktop-work-to-code/acceptance/`. No run of the lane's real tick over a simulated day | none |
| The ticket lane (`list_dispatch.py`) | WOULD BENEFIT | `src/RimMandrake/rimflow/selftest_list_dispatch.py`: fixture cases, one decision each | none |
| The Maturation Pipeline tick (`maturation_dispatch.py`) | WOULD BENEFIT | `selftest_maturation_dispatch.py` and its family: fixture cases. A seed: `forecast` (`maturation_dispatch.py next --within`) runs the real `_tick` in its dry pass with the clock moved step by step over one observation of the world. It forecasts launches; it does not vary the world or hunt faults | the seed is real code |
| The publish door and clone levels (`./publish`, `land.sh`, `seat_sync.py`, the tree checks of `publish_tree_checks.json`) | WOULD BENEFIT | `selftest_publish_tree_checks.py`, `selftest_polish_door.py`, `selftest_dispatch_clone_sync.py` (real git against a local bare origin, the real `land.sh` and `seat_sync.py`): fixed cases, not many writers in random order | none |
| The work bundles (`work_bundle.py`) | WOULD BENEFIT | `selftest_work_bundle.py`, `selftest_work_bundle_monitor.py`: fixture cases | none |
| The game locks (`game_lock.py`) | WOULD BENEFIT | `selftest_game_lock.py` and two Windows variants: fixed cases | none |

## The faults behind each WOULD BENEFIT row, ranked by hours

A simulation "would have shown" a fault when the fault is a state that nothing ends, a loop that does not stop, or a
reading of an input kind that the stand-ins can make. A fault of the environment (a stale DLL, a CPU fault, a driver)
is not counted: a simulation would not have shown it.

### Rank 1: the SteveDesktop test lane, about 64 h

| fault | hours | source |
|---|---|---|
| A lane pause with no end stood 49.3 h, 2026-11-15 6 AM to 2026-11-17; asked jobs waited 142.7 h under pauses in 21 days | 49.3 | `design/specs/2026-11-23-stevedesktop-work-to-code/analysis.md`; `RIMMANDRAKE_END_EVERY_LANE_PAUSE_ITSELF_FORTYNINE_HOURS` |
| Steve2 gave the same refusal 47 times in 11 hours, 2026-11-23 | 11 | `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` |
| The SteveDesktop account gate refused every launch for 3.6 h on 2026-11-26: it counted runs that it could not read as live | 3.6 | `design/specs/2026-11-26-stuck-items-study/one_page.md` |
| Not counted: 50 jobs on a stale bridge DLL, 26 mod lists that could not be written (environment and deploy, not lane logic) | - | same study |

### Rank 2: the ticket lane, about 57 h

| fault | hours | source |
|---|---|---|
| A block on a finished ticket read as a block for good: 40 open items, the chain stood still 16 hours (2026-11-24) | 16 | `RIMMANDRAKE_LIFT_LANE_BLOCK_WHEN_PREDECESSOR_IS_DONE` |
| 4 tickets stopped by the chain limit with no next step, ages 31 to 39 h at the 11:23 AM tick of 2026-11-26 | 39 | `design/specs/2026-11-26-stuck-items-study/one_page.md` |
| The machine-load line held the lane 2.2 h in 81 h | 2.2 | same study |
| Old tickets entered the lane only when a hand named them: the tick launched nothing at 10:42 and 10:52 PM PST 2026-11-25 | UNMEASURED | `RIMMANDRAKE_NAME_OLD_PIPELINE_TICKETS_BY_PROGRAM_FEED_RAN_DRY` |
| The lane sent a run to SteveDesktop only when Archmagi's slots were full, so SteveDesktop sat idle with work waiting (2026-11-26) | UNMEASURED | `RIMMANDRAKE_SEND_PIPELINE_TICKETS_TO_STEVEDESKTOP_FIRST_IT_SAT_IDLE` |

### Rank 3: the Maturation Pipeline tick, about 53 h

| fault | hours | source |
|---|---|---|
| A mod that rests after its pass keeps its open mod tickets: Gimme Some Slack 45 h and Pyrelands 41 h at rest, 5 tickets, 146 ticket-hours | 45 | `design/specs/2026-11-26-stuck-items-study/one_page.md`, proposal 4 |
| Steve2's refused loads were counted as visit-chain failures: 6 FlowWorks visit chains spent, the visit feed quiet about 6 h (2026-11-22 to 2026-11-23) | 6 | `RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER` |
| A stale walk build's deploy went to a steward that may not stop the game: the steward waited 2 h for ArchBig, 5:16 to 7:37 AM PST 2026-11-24 | 2 | `RIMMANDRAKE_LET_TICK_DEPLOY_STALE_WALK_BUILD_STEWARD_MAY_NOT_STOP_GAME` |
| The road-back hold read `blocked` with both games free and launched nothing on Explosive Knockback (seen 3:52 to 4:00 PM PST 2026-11-25) | 0.1 seen | `design/specs/2026-11-25-tick-launches-road-back-hold/boundary.md` |
| Not counted as stuck work: the same chain-cap hold rang a second alarm for about 13 h (2026-11-16) | - | `RIMMANDRAKE_SKIP_CHAIN_CAPPED_CONCEPTS_IN_DESIGNER_STALL` |

### Rank 4: the publish door and clone levels, about 22 h

| fault | hours | source |
|---|---|---|
| Refused closes whose only text is the publish's "nothing to publish": 7 tickets, ages up to 15 h, 62 ticket-hours in 81 h | 15 | `design/specs/2026-11-26-stuck-items-study/one_page.md`, proposal 6 |
| A role clone held a twin ledger commit and staged twin files for 3 h while every landing said ok and level (2026-11-21) | 3 | `RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL` |
| The timers' clone was stuck 2.5 h on an untracked duplicate of a file already upstream (measured the evening of 2026-11-16 PST) | 2.5 | `RIMMANDRAKE_HOLD_SIX_BIOME_MODS_ONLY_PYRELANDS_STAYS` (its evidence) |
| The dispatch clone sat 47 to 49 behind from 11:41 AM to 12:20 PM PST 2026-11-15: `pull --rebase` refused on the other writer's unstaged shard line, so every timer ran stale code | 0.65 | `RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE` |
| The tick's clone did not pull from 9:35 AM PST 2026-11-26 (68 behind at 10:01 AM): two lines that no landing carried blocked the pull, so the tick read a passed mod as still at his walk | 0.5 | `RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL` |

### Rank 5: the work bundles, about 10 h

| fault | hours | source |
|---|---|---|
| After the bundle code (11:52 PM PST 2026-11-24) every lane run was a bundle, and a bundle ran on Archmagi only: no lane run reached SteveDesktop from 12:47 AM to 10:58 AM PST 2026-11-25 | 10.2 | `RIMMANDRAKE_SEND_LANE_BUNDLES_TO_STEVEDESKTOP_NONE_SINCE_ONE_AM` |
| The automatic launcher made bundles of one ticket: 10 of 12 bundle files at 11:15 AM PST 2026-11-25 | UNMEASURED | `RIMMANDRAKE_BUNDLE_LIST_TICKETS_BY_HOME_TEN_OF_TWELVE_HELD_ONE` |
| Not counted: 2 tickets left out of their bundle, 484 h since their last progress; most of that age is from before bundles existed | - | `design/specs/2026-11-26-stuck-items-study/one_page.md` |

### Ranked last: the game locks, hours UNMEASURED

| fault | hours | source |
|---|---|---|
| An OWNER driver lock whose holder process was gone refused every take after he released his hold (2026-11-16 6:55 AM PST) | UNMEASURED | `RIMMANDRAKE_FREE_DEAD_OWNER_DRIVER_LOCK_BLOCKS_EVERY_TAKE` |
| A 9-hour-old mod-list swap marker of a dead process blocked a mod-list write on ArchBig (3:38 AM PST 2026-11-25); a 3-day-old one refused a tier on ArchSmall (4:31 AM PST 2026-11-25) | UNMEASURED | `RIMMANDRAKE_CLEAR_STALE_MODLIST_SWAP_MARKER_FOURTH_TIME_BY_HAND`, `RIMMANDRAKE_CLEAR_STALE_SWAP_MARKER_NOBODY_OWNS_ARCHSMALL_LIST` |
| A mod lease: a second road-back fixer that never started fenced the live holder, so its renewals were refused (Explosive Knockback, 2026-11-17) | UNMEASURED | `RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED` |

## Other simulations found on the way (not rows)

- `src/RimMandrake/Utils/selftest_await_lifecycle.py`: the game-load wait over a fake bridge and a fake clock.
- `design/specs/2026-11-25-offline-real-game-code-probe/`: which game code runs offline; a headless real game on
  SteveDesktop (a real game, so not offline).
- `design/RimMandrake/mod_deepdive_yayo_{acc,armor,full}_sim.py`: worked numbers for a third-party combat mod.
- `src/RimMandrake/Pyrelands/selftest_pyrelands_burn_ecology.py` and two burn selftests read `pyre_burn_sim.py`.

## What the census could not look at

- Codex runs, and hours that no record carries.
- For each HAS ONE mod, which of its live faults in the window a caller simulation would have caught.
- Whether each existing simulation still runs green today: the census read the files and ran none of them.
