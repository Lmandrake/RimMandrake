# BOUNDARY: the scene run in the tick (BRIDGE v2.0), Design Version 0.2.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneTickCore.cs` (all of it),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneTick.cs` (all of it), and the scene lines of `TickPre`,
`TickPost`, `TickFin` and `Frame` and the condition run of `JawaBenchSafeAdvance` in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs`.
Items: `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`, `RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK`. Design: `05_build_design.md` beside this page. Each promise
has a test of its name in `src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py`. The live proof is
`src/RimMandrake/bridgetools/prove_scene_tick_wiring.py`.

One run: tracks (named probes), act steps (each on a tick counted from the start), one end condition, a tick limit. The game
plays it in its own loop (PLAY). The run is stepped at the end of each tick, in this order: **sample, conditions, end test,
act steps**. The run judges nothing.

`jawa/scene_slice` (TEST profile only) is the one hand-written scene: probes on one pawn, one damage act, one end condition.
`cancel` ends a live standalone slice. While a session is open or closing, the slice tool allows `status` and refuses
`start` and `cancel`. The session driver uses `jawa/run_until` to cancel. The hands page's
`only-the-driver-drives-an-open-session` check covers this guard.
`jawa/run_plan` (`RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`) replaces the tool and keeps the run.

## THE TRACE (schema `scene_trace_v1`)

Each record is one line of kind `scene` in the game's `JawaBench` record, written by `JawaBenchTpsWriter`. The line's own
`seq` is the order of the records of the run and of every tap. The fields of a scene line:

| field | meaning |
|---|---|
| `run` | the run's id |
| `n` | the row's number inside the run, from 1, with no gap. A gap is a lost row |
| `tick` | `TicksGame` when the record was made |
| `phase` | `first` (before any act), `end_of_tick`, `last` (after the pause), `in_tick` (a `mod` record, written during the game's tick) |
| `rec` | `open`, `track`, `act`, `fault`, `mod`, `end`, `close` |

- `open`: `schema`, `mode` (`PLAY`; `STEP` when a step loop drives the tick, and `speed` then names the loop), `speed`, `epoch`, `cond` (the condition as compiled, with its tracks), `acts`,
  `maxTicks`.
- `track`: `name`, `st` (`ok`, `gone`, `oob`, `unbound`, `error`), `v`, and `detail` when `st` is not `ok`. Written at `first`
  and `last` for every track, and at `end_of_tick` only when `v` or `st` changed.
- `act`: `name`, `ok`, `detail`. Written after the act step was done, on the tick on which it was done.
- `mod`: `mod` (the assembly), `name`, and `key` and `v` when the mod gave them. A mod's `RMTrace.Emit` while the run runs; evidence of a
  branch only. The sinks and their promises: `../2026-11-23-bridge-v2-mod-hooks/boundary.md`.
- `fault`: `what` (`rand_in_sample`, `ran_past_end`, `pause_refused`, `game_replaced`, `threw`), `detail`.
- `end`: `state` (`hit`, `unknown`, `done`, `stopped`, `error`, `epoch`, `cancelled`, `aborted`, `threw`, `budget`), `hitTick`, `executed`, `why`,
  `triggers`, `unknown`, `complete`, `cost`, `costliest` (the condition node or track whose reads took the most time).
- `close`: `rows`, `dropped`, `drained`, `paused`, `tickAfter`, `skipped`, `randFaults`, `actsNotDone`, `alloc`, `lockReads`, `breaches` (tool -> refused calls). The last
  record of a run. A trace with no `close` is incomplete.

## THE EVIDENCE CONTRACT (what a judge may assume; each point that fails is COULD NOT LOOK)

1. The order inside a tick is the fixed one, so a value that an act changed is sampled on the next tick at the latest, and a
   run cannot end before that sample.
2. Every track has a first sample before any act and a last sample after the pause.
3. Every record has its sequence number, its tick and its phase. An act writes its own record.
4. Loss is counted in `close`. `drained` false, `dropped` above 0 or a gap in `n` means that the trace is not whole.
5. A sampled value is an end-of-tick value.
6. A random draw inside the sample phase is a `fault` record.

Not yet in the trace, each with its ticket in `06_build_order.md`: the plan and checker versions; the reviewed list of readers (a track may read a property today).

## THE LIFE CYCLE, THE RUN LOCK

On their own page: `design/specs/2026-11-23-bridge-v2-life-cycle/boundary.md`.

## LIMITS

- **60 s for the writer to drain, then `close` says `drained` false.** Danger: a full or dead disk leaves the run open for
  ever, and no later run can start.

## DOES NOT SURVIVE (not promised)

- The faults of a run from outside its tick: `../2026-11-23-bridge-v2-life-cycle/boundary.md`.
- **a-value-that-changes-twice-in-one-tick.** Only its last state is seen.
- **zero-allocation-with-a-changing-number.** A number that changes every tick (`game.tick`) costs one 24-byte box a tick, and
  a condition over a rectangle allocates its cells.

## PROMISES (each one is owed a test of the same name)

- **a-hit-on-tick-t-executes-t.** A condition that turns true at the end of tick T ends the run on T, and the game runs no
  tick after T.
- **true-at-arm-executes-nothing.** A condition that is true at the start ends the run with `executed` 0.
- **a-track-writes-on-change-only.** One row for each change, none without a change.
- **gone-is-gone-never-zero.** A track whose subject is gone writes `gone` with a null value.
- **an-unknown-ends-the-run-as-unknown.** Under `on_unknown: stop`, an unreadable condition ends the run in state `unknown`.
- **a-skipped-original-records-nothing.** A tick that another mod skipped writes no row and is counted.
- **the-close-counts-the-dropped-and-waits-for-the-drain.** `close` is written after the writer drained, and counts each row
  that the writer refused.
- **sample-before-act-inside-a-tick.** On a tick that samples a change and does an act, the sample has the lower sequence.
- **an-act-and-the-end-never-share-a-tick.** An act that is due on the tick of the end is not done, and `close` names it.
- **first-and-last-sample-of-every-track.** Both exist, also when the run ends at the start.
- **a-draw-in-the-sample-phase-is-reported.** A random draw there is a `fault` record and is counted.

Later lists beside this page: `polish.md`, `next_version.md` (none yet).

## Offline judge

The judge uses this trace and the matching `s.run` receipt from the kept folder. It checks the envelope, loss,
sample order and coverage, observation names and alias continuity before classifying. It reports the classifier
row and the first failed condition with recorded values. A keeper can be judged again from the same evidence.
The first verdict stays in place and an accepted rejudgement appends one history line. The named tests and the
offline input contract are on the [scene judge boundary](../2026-11-23-scene-judge/boundary.md).
## Verdict ledger

`src/RimMandrake/rimflow/scene_verdicts.py` turns the runs of one claim on one build into the scene's verdict, from
`design/concepts/<Mod>/version/scene_runs.jsonl`. A run whose receipt has an overlay stamp, the taint mark, an
uncompared arm, a PROOF build or a map kind that the bar does not accept counts for no bar. The Stage 6 exit keeps a
check's pass only when the ledger reads PASS or has no line for its scene. The promises and tests are on the
[verdict ledger boundary](../2026-11-23-scene-verdicts/boundary.md).
## GAME WATCHER

`src/RimMandrake/Utils/game_watcher.py` reads the existing TPS heartbeat and the named game's process identity.
It names ticking, paused, stopped frames, consecutive frame exceptions, a stuck load, menu, no map and process gone.
A missing, unreadable or old-format heartbeat is COULD NOT LOOK and adds one line to the scene receipt. Scene
admission checks the disk reading before connecting and before starting a run, and refuses a game read as broken
or gone. A broken-game stop goes through `game_instance.py stop --broken` after two independent readings.
The [watcher boundary](../2026-11-23-bridge-v2-watcher/boundary.md) names the tests, limits and stop evidence.

## CAST TRACKS AND JOB TAPS

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCastCore.cs` (all of it, the pure half),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCast.cs` (all of it, the Verse half and its three patch sites), the `ISceneCast`
seam of `JawaBenchSceneTickCore.cs`, `CastPawns` and the `JawaBenchCast.Join` line of `JawaBenchHands.cs`, and the `kill-cast` line of
`KillPostfix` in `JawaBenchSituationalTools.cs`. Item `RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY`. Each promise has a test of
its name in `src/RimMandrake/bridgetools/selftest_cast_tracks.py` (harness `bridgetools/CastTracksSelfTest`). The hooks are on
`src/RimMandrake/bridgetools/HOOKS.md`.

**The cast** of a `jawa/run_until` run is every pawn of the session's bindings: an alias, or `alias[i]` in a group. Each member has the
twelve standard cast tracks, `<alias>.pos`, `facing`, `job` (`def#loadID`), `toil`, `health` (summary percent), `downed`, `dead`,
`mental`, `carried`, `holder`, `faction` (`def#loadID`), `drafted`. They are sampled in the sample phase, after the named tracks, and
written on change only, as `track` rows of the trace (first and last sample of every one).

**The taps** (lazy: on at the first run with a cast, then on): job start (`Pawn_JobTracker.StartJob`), job end
(`Pawn_JobTracker.CleanupCurrentJob`, where every end goes, `EndCurrentJob` and the end inside `StartJob` included), and a reservation
made or refused (`ReservationManager.Reserve`). The kill tap that exists feeds the cast too. A tap row is a scene line with phase
`in_tick` and the run's own `n`; it carries `ord`, the entry ordinal taken at the prefix (the call order, also when calls nest).

| rec | fields |
|---|---|
| `job_start` | `alias`, `thing`, `ord`, `job`, `def`, `giver` (the ThinkNode type, `player`, `queue` or `direct`), `current`, `prev` (the job it replaced), `prevEnd` (its end condition, or `Suspended`) |
| `job_end` | `alias`, `thing`, `ord`, `job`, `def`, `toil` (the toil it ended on), `cond` |
| `reserve` | `alias`, `thing`, `ord`, `job`, `target`, `made`, `holder` (who holds it, when refused) |
| `kill` | `alias`, `thing`, `ord`, `culprit` |
| `link` | `alias`, `from`, `to`, `why`: the alias moved to another thing (a dead pawn's corpse) |
| `rebind` | `name` (`<alias>.toil`), `from`, `to`: the job of the toil track changed |
| `reconcile` | `alias`, `what`, `deadAt`, `verdict` (`COULD NOT LOOK`) |

`close` gains `cast`: `members`, `tracks`, `samples`, `reads`, `rows`, `links`, `rebinds`, `ms`, `msMax`, `msPerTick`, `reconcile`, and
`taps` (`records`, `outside`, `notCast`, `dropped`, and the coverage of each of the three hooks).

### LIMITS

None of its own. The taps use the guards of `JawaBenchHookGuard`; the rows go through the writer of the run.

### DOES NOT SURVIVE (not promised)

- **a-hook-that-is-not-connected.** An offline test proves the rules, never that Harmony put the hook on the method or that another mod's
  prefix lets the original run. The live proof is the tap certificate (`RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`).
- **a-change-inside-one-tick.** A cast track sees the end of the tick. A job that started and ended inside one tick is seen only by the taps.
- **zero-allocation-with-a-cast.** A changed position, job or holder text costs one string; a tap row costs its line.
- **a-pawn-outside-the-cast.** Its jobs and reservations are counted (`notCast`) and not written.

### PROMISES (each one is owed a test of the same name)

- **the-job-tap-follows-the-six-hook-rules.** Reentrancy, a skipped prefix, a skipped original, a game exception, an off-thread call and
  a writer fault are each handled as `HOOKS.md` says, for the job start and the job end; a job start names the job it replaced and its
  end condition, and the end row comes first.
- **the-reservation-tap-follows-the-six-hook-rules.** The same six, for a reservation; a refusal names its holder.
- **two-job-starts-in-one-tick-keep-their-order.** Rows of one tick keep their record order in `n`, and `ord` keeps the call order when
  one start nests inside another.
- **a-record-outside-any-run-is-dropped-and-counted.** With no running run (none, or one that is settling), a tap writes no row and counts
  it in `outside`.
- **an-alias-whose-object-is-replaced-writes-a-link.** An alias never moves to another thing without a `link` row before the rows of that
  thing.
- **a-track-on-a-replaced-job-rebinds.** When the job changes, a `rebind` row and then the toil row are written, also when the index is
  the same.
- **the-settle-reconciliation-catches-a-death-with-no-kill-record.** A cast member that died in the run with no kill record is a
  `reconcile` row, verdict COULD NOT LOOK, and is listed in `close`.
- **the-hook-table-check-passes.** `selftest_bridge_hooks.py` passes with the three new sites on `HOOKS.md`.
- **the-per-tick-cost-of-the-tracks-is-in-the-result.** `close.cast` holds the ms of the cast tracks, the most of one sample and the
  mean per tick.

## WORLD EVENT TAPS AND WORLD TRACKS

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldCore.cs` (all of it, the pure half),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorld.cs` (all of it, the Verse half and its nine patch sites), the `World`
seam of `JawaBenchSceneTickCore.cs`, the `JawaBenchWorld.Join` line of `JawaBenchHands.cs`, and `AliasNow` in `JawaBenchCast.cs`. Item
`RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY`. Each promise has a test of its name in
`src/RimMandrake/bridgetools/selftest_world_taps.py` (harness `bridgetools/WorldTapsSelfTest`). The hooks are on
`src/RimMandrake/bridgetools/HOOKS.md`.

**The world tracks** of a `jawa/run_until` run read the run's map: `world.weather` (the current weather def), `world.conditions` (the
active game conditions of the map and of the world, by def, sorted), `world.temp` (outdoor temperature, to 0.1 °C), `world.hour`
(local hour), `world.camera` (the view rectangle and the zoom, or `elsewhere` when the camera is on another map) and `world.windows`
(the window stack, bottom to top, by type). They are sampled in the sample phase after the cast tracks and written on change only, as
`track` rows (first and last sample of every one). A map that is gone is a row with `st` `gone`.

**The taps** (lazy: on at the first run, then on). A tap row is a scene line with phase `in_tick` and the run's own `n`; it carries
`ord`, the entry ordinal taken at the prefix. A pawn or thing of the cast carries its alias.

| rec | hook | fields |
|---|---|---|
| `mental_attempt` | `MentalStateHandler.TryStartMentalState` | `thing`, `alias`, `ord`, `state`, `reason`, `forced`, `started`, `prev` (the state before the call) |
| `mental_start` | the same call, when it started a state | `thing`, `alias`, `ord` (the attempt's), `state`, `now` |
| `quest` | `QuestManager.Add` | `ord`, `quest` (id), `root`, `name`, `added`, `refused` (`already there`, `not added`), `accepted` |
| `letter` | `LetterStack.ReceiveLetter(Letter, ...)`, where the other two overloads go | `ord`, `def`, `label`, `delay`, `queued`, `shown`, `quest`, `targets` |
| `message` | all four `Messages.Message` overloads; the outermost call writes | `ord`, `text`, `def`, `shown`, `hidden` (the repeat rule), `targets` |
| `fire` | `Fire.SpawnSetup`, where both fire routes go; not a fire a load restores | `ord`, `fire`, `cell`, `size`, `attached`, `attachedAlias`, `instigator`, `instigatorKind` (`pawn`, `thing`, `none`), `instigatorAlias` |
| `explosion` | `GenExplosion.DoExplosion` | `ord`, `cell`, `radius`, `damage`, `instigator`, `instigatorKind`, `instigatorAlias`, `weapon`, `projectile` |

`close` gains `world`: `tracks`, `samples`, `reads`, `rows`, `ms`, `msMax`, `msPerTick`, and `taps` (`records`, `outside`, `dropped`,
`innerMessages`, `loadedFires`, and the coverage of each of the six hooks).

### LIMITS

None of its own. The taps use the guards of `JawaBenchHookGuard`; the rows go through the writer of the run.

### DOES NOT SURVIVE (not promised)

- **a-hook-that-is-not-connected.** An offline test proves the rules, never that Harmony put the hook on the method, that a small
  `Messages.Message` overload was not inlined into a caller compiled before the patch, or that another mod's prefix lets the original
  run. The live proof is the tap certificate (`RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`).
- **a-change-inside-one-tick.** A world track sees the end of the tick. A window that opens and closes in a frame with no tick is not
  seen (the window stack is sampled at each tick, not each frame).
- **events-of-the-whole-game.** The taps record every event while a run is running, on any map. A judge filters by cell, alias or map.

### PROMISES (each one is owed a test of the same name)

- **the-mental-tap-follows-the-six-hook-rules.** Reentrancy, a skipped prefix, a skipped original, a game exception, an off-thread call
  and a writer fault are each handled as `HOOKS.md` says, and a record outside any running run is dropped and counted in `outside`.
- **the-quest-tap-follows-the-six-hook-rules.** The same, for a quest; a quest that was there already is a row with `added` false.
- **the-letter-tap-follows-the-six-hook-rules.** The same, for a letter; a delayed letter is `queued`, not `shown`.
- **the-message-tap-follows-the-six-hook-rules.** The same, for a message, with the guard's depth closed by the finalizer; the nested
  overloads write one row.
- **the-fire-tap-follows-the-six-hook-rules.** The same, for a fire; a fire lit by a pawn and one lit by a thing name their instigator
  and its kind; a fire that a load restores is counted, not written.
- **the-explosion-tap-follows-the-six-hook-rules.** The same, for an explosion, with its instigator.
- **an-attempt-and-a-start-are-two-records.** Every attempt is a `mental_attempt` row, started or not; a start is also a `mental_start`
  row with the attempt's `ord`, written after it.
- **a-message-is-recorded-before-the-rule-that-hides-repeats.** A message that the repeat rule hides is still a row, with `shown` false.
- **the-hook-table-check-passes.** `selftest_bridge_hooks.py` passes with the nine new sites on `HOOKS.md`.
- **the-world-tracks-write-on-change-and-their-cost-is-in-the-result.** One row per change of each world track, and `close.world` holds
  their ms, the most of one sample, the mean per tick and the six taps' coverage.

## SCENE GATES

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGatesCore.cs` (all of it, the pure half),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchGates.cs` (all of it, the Verse half and its two patch sites), the gate
call in `JawaBenchAwareness.IncPre` (the incident gate sits on that present hook, no site of its own), and `JawaBenchWorld.LiveSink`.
Item `RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE`. Each promise has a test of its name in
`src/RimMandrake/bridgetools/selftest_scene_gates.py` (harness `bridgetools/GatesSelfTest`). The hooks are on
`src/RimMandrake/bridgetools/HOOKS.md`.

**Three gates**, each a mechanism for the calm profile (`RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE` joins them into a
profile with its lease and its tool call; this ticket gives them no tool of their own):

| gate | where | the name on the allow list | a held attempt |
|---|---|---|---|
| `incident` | `IncidentWorker.TryExecute`, decided first inside the awareness prefix `IncPre` | the incident def | `TryExecute` returns false; the worker never runs; the incident journal row reads `workerEntered` false, "held by the scene incident gate" |
| `quest` | a prefix on `QuestManager.Add` | the quest's root def | the quest is not added |
| `mental` | a prefix on `MentalStateHandler.TryStartMentalState` | the mental state def | the call returns false, as the game's own refusals do |

`JawaBenchGates.Arm(kind, allow)` arms one gate for the game now loaded, on the main thread. While armed, every attempt that reaches
the gate is counted. An attempt whose name is on the allow list goes through and uses up that entry: a name listed once goes through
once, a name listed twice goes through twice. Every other attempt is held, counted and logged with its caller (the first stack frame
that is not ours, not Harmony's replacement and not the gated method), its tick and a detail; while a run is running it is also a
`gate` row of the run's trace (`gate`, `outcome` `held` or `allowed`, `name`, `caller`, `detail`, `gseq`, `gtick`). An off gate
returns at once. A gate whose game changed, or whose game is now under a canonical save, lets the attempt run and releases itself,
with the reason in `lastRelease`.

**The incident queue held aside.** `JawaBenchGates.HoldQueue` copies every entry of the storyteller's incident queue aside, with its
fire tick and the end of its retry window as absolute ticks, and empties the queue. `GiveBackQueue` puts each entry back with both
ticks moved by the ticks held, so an entry keeps its distance to its fire tick and the length of its retry window (`retryDurationTicks`
is unchanged; a return that moved the fire tick only would leave a tried entry past its window at once). An entry that was already
past its retry window when it was held (tried, and `fireTick + retryDurationTicks` at or before the hold tick: the engine drops it
on its next tick) is named at the hold and at the give-back, and is not given back. A give-back into another game returns nothing
and names each entry.

### LIMITS

- **the gate log: 200 rows per gate.** The danger: a gate left armed on a busy map grows without end. The counts stay exact; a row
  pushed out is counted in `rowsDropped`.

### DOES NOT SURVIVE (not promised)

- **a-hook-that-is-not-connected.** An offline test proves the rules, never that Harmony put the prefixes on the methods, or that
  another mod's prefix with a higher priority did not run first. The live proof is the tap certificate
  (`RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`), which shows a held route and a refused route for each gate.
- **a-route-around-the-gated-method.** A mental state set without `TryStartMentalState` (a load restores one), a quest put in the
  manager without `QuestManager.Add`, or an incident body that a mod runs without `IncidentWorker.TryExecute` is not gated.
- **the-offer-letter-of-a-held-quest.** `QuestUtility.GenerateQuestAndMakeAvailable` returns the quest whatever `Add` did, so its
  caller can still send the offer letter. The letter tap records it.
- **a-driver-that-never-gives-back.** A gate and a held queue stay until released, given back, a load or a new game. A driver that
  dies leaves them on; the lease is the calm profile ticket's. A save made while the queue is held saves it empty.
- **entries-queued-while-held.** An incident queued while the queue is held stays in the queue and fires by its own ticks.
- **a-call-from-another-thread.** It runs, and is counted in `foreignPassed`; the gates decide on the main thread only.

### PROMISES (each one is owed a test of the same name)

- **the-allow-list-lets-one-named-incident-through-once.** An incident named once on the allow list runs once; the same incident
  again, and any other, is held. The incident gate is decided inside `IncPre`, which returns false and sets the result false for a
  held incident.
- **a-held-attempt-is-counted-and-recorded-with-its-caller.** Each held attempt adds one to `held` and `attempts`, and is a log row
  and a trace row that name the gate, the name, the caller and the tick. A caller that cannot be read reads `unknown`.
- **a-gate-that-is-off-changes-nothing-and-records-nothing.** An off or released gate lets every call run, counts nothing, logs
  nothing, writes no row and reads neither the caller nor the detail.
- **a-held-queue-entry-comes-back-with-its-fire-tick-moved.** Each entry given back has its fire tick moved by the ticks held, and
  keeps its tried flag.
- **a-held-queue-entry-comes-back-with-its-retry-window-moved.** Each entry given back has the end of its retry window moved by the
  same ticks, so its retry duration is unchanged and a tried entry is not past its window at once.
- **an-entry-past-its-retry-window-when-held-is-reported-never-dropped-in-silence.** Such an entry is named at the hold and at the
  give-back, and counted in `expired`; every entry held is given back or named.
- **the-quest-gate-follows-the-hook-rules.** The quest prefix: an off gate first, then the thread (a foreign call runs, counted, reads
  nothing), then an original that another prefix already skipped (not held, counted), then the decision; a nested attempt is decided
  on its own; a fault of ours is counted and never lets a held attempt through, nor throws into the game; a dropped row and a row
  outside any run are counted; a game change releases the gate. The prefix is on `HOOKS.md`, and `selftest_bridge_hooks.py` passes.
- **the-mental-gate-follows-the-hook-rules.** The same, for the mental prefix, which also sets the result false for a held attempt.
- **with-a-canonical-save-loaded-every-gate-is-refused.** Under CAMPAIGN, arming each of the three gates and holding the queue is
  refused by name and changes nothing, and a gate armed on a test save lets go when a canonical save is loaded under it.

## TAP CERTIFICATE

Code: `src/RimMandrake/bridgetools/tap_certificate.py` (all of it: the pure core and the `audit` command), the witness counts of
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchHookGuard.cs` (`Committed`, `Mark`, and `committed`, `runEntered`,
`runCommitted` in `CoverageFields`), the `Mark` calls in `JawaBenchCastCore.Taps.NewRun` and `JawaBenchWorld.Join`, and the live
session `src/RimMandrake/bridgetools/prove_tap_certificate.py`. Item `RIMMANDRAKE_BUILD_TAP_CERTIFICATE_CANARY_RUNS_OFF_STAGE`. Each
promise has a check of its name in `src/RimMandrake/bridgetools/selftest_tap_certificate.py`. No new patch site.

**The certificate** is made once for each loaded identity, in a disposable game, by `prove_tap_certificate.py`: route fixtures do
each tapped act by its real engine route, a positive and a negative case each, and one hook is taken off by hand and must be reported
blind. It holds, for each tap of `TAPS`: the routes shown, the routes not shown, and every other owner's patch on its methods. Its
key is the MVID of `JawaBench.BridgeTools` as loaded, the fingerprint of the running mod list (`loaded_build.fingerprint`), the hash
of every other owner's patch on a tapped method, and the hash of the settings of every mod that has such a patch.

**The check at arm** (`arm_check`) reads the loaded identity with `jawa/running_mods` and `jawa/harmony_patches` only (`ARM_READS`),
and does no act. A scene arms CERTIFIED only when the certificate's key equals the loaded identity, our patch is on each method of
each tap that it needs, and each route that it needs is on the certificate's shown list. Else it is COULD NOT ARM (a difference, a
route not shown, our hook not on the method) or COULD NOT LOOK (no certificate, a read that failed), and its receipt reads
BOOTSTRAP. The receipt names each foreign prefix on a method of a tap that the scene needs.

**The witness** (`witness`, `run_coverage`) reads a run's close record: for each hook of `cast.taps` and `world.taps`, `runEntered`
(admitted entries since the run's `Mark`) against `runCommitted` (postfixes that ran on an admitted call whose original ran). An entry
with no commit (the original was skipped, it threw, or the postfix did not run) voids that tap's coverage for the run.

### LIMITS

None of its own.

### DOES NOT SURVIVE (not promised)

- **a-foreign-prefix-that-acts-otherwise-this-run.** No check at arm can show that another mod's prefix acts in this run as it did in
  the session. An absence on such a method reads "not provable here", and a judge uses it neither to excuse nor to convict.
- **a-route-the-session-did-not-take.** A route that no fixture took is "not shown", and an event on it can come and go unseen.
- **the-marker-row.** The arm check sends no marker row through the writer: the run's own first sample is the first row that the
  writer acknowledges, and a run whose trace has no first sample is COULD NOT LOOK by the evidence contract.
- **a-hook-with-no-prefix-entry.** The witness counts only admitted entries. A hook whose prefix never ran (our patch off) shows no
  gap; the arm check's patch read and the session's blind plant catch that case.
- **gates-and-the-kill-and-incident-taps-in-the-witness.** They have no `runEntered`/`runCommitted` row in the close record; their
  coverage for a run rests on the certificate alone.

### PROMISES (each one is owed a test of the same name)

- **a-certificate-for-another-companion-is-refused.** A loaded companion MVID that differs from the key refuses the certificate.
- **a-certificate-for-another-mod-list-is-refused.** A running mod list whose fingerprint differs refuses it.
- **a-changed-patch-inventory-is-refused.** Another owner's patch added to, or taken off, a tapped method refuses it.
- **a-route-not-shown-is-listed-never-covered.** A route that no fixture showed is on `not_shown` and never on `covered`.
- **a-scene-that-needs-an-uncertified-tap-could-not-arm.** A needed route not shown, or a tapped method without our patch, is COULD NOT
  ARM, and the receipt reads BOOTSTRAP; a scene whose every need is covered reads CERTIFIED.
- **the-arm-check-calls-no-act.** The arm check calls only `ARM_READS`, and none of them is on the session's act list (`ACT_TOOLS`).
- **a-foreign-prefix-is-named-on-the-receipt.** Each foreign prefix on a method of a needed tap is a receipt line with its owner.
- **a-missing-certificate-is-could-not-look.** No certificate is COULD NOT LOOK on every need, never covered, and BOOTSTRAP.
- **a-changed-setting-of-a-patching-mod-voids-the-certificate.** A changed settings hash of a mod with a patch on a tapped method
  refuses the certificate; a setting of a mod with no such patch changes nothing.
- **an-entry-with-no-record-voids-the-tap-for-the-run.** A hook with more run entries than run commits voids its tap for the run; a
  hook row without the two counts is "could not look", never "ok".
- **an-absence-under-a-foreign-prefix-is-not-provable-here.** An absence on a covered route of a method with a foreign prefix reads
  "not provable here"; on a route not shown it reads "not covered".

## LIVE READINGS

| proof | reading | evidence |
|---|---|---|
| `prove_stage_map.py` | 6 of 6 rows PASS: R1, R2, R5, R6 on ArchSmall (2026-11-24, `design/specs/2026-11-23-bridge-v2/live/stage_map/prove_stage_map_2026-11-24.txt`); R3, R4 on ArchBig under the raid allow, the raid held still by `jawa/fire_raid` ImmediateAttack/EdgeWalkIn, R4 the repaired claim above (2026-11-25, `design/specs/2026-11-23-bridge-v2/live/stage_map/prove_stage_map_r3r4_2026-11-25.txt`) | the two files named |
| `prove_run_life_cycle.py` | 3 of 3 rows PASS | `design/specs/2026-11-23-bridge-v2-life-cycle/live/` (ArchSmall, tier `explosiveknockback_visit`, companion and Explosive Knockback PROOF build from `ac24cfedbb`, 2026-11-24) |

## PLAY AGAINST STEP

`scene.py compare` (`src/RimMandrake/Utils/scene_compare.py`) has its own page: `design/specs/2026-11-24-play-vs-step/boundary.md`.

## THE STAGE READ-BACK (`JawaBenchStageReadBack.cs`)

Items `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO` and `RIMMANDRAKE_WIRE_PAWN_KIT_TOOLS_REPLY_FROM_READ_BACK`.
Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStageReadBack.cs`
(all of it, pure, no RimWorld type), and its calls in `jawa/set_terrain_batch`, `jawa/destroy_batch`, `jawa/spawn_pawn`
(`JawaBenchTerrainTools.cs`), `jawa/build_batch` (`JawaBenchMapTools.cs`), `jawa/pawn_gear`, `jawa/pawn_traits`,
`jawa/set_pawn_skill`, `jawa/pawn_need`, `jawa/pawn_health` (`JawaBenchPawnTools.cs`), and `jawa/set_work_priority`
(`JawaBenchJobTools.cs`). Each promise has a test of its name in `src/RimMandrake/bridgetools/selftest_stage_ops.py`
(harness `src/RimMandrake/bridgetools/StageOpsSelfTest/`). The map staging live proof is
`src/RimMandrake/bridgetools/prove_stage_ops.py`. Pawn kit live rows still need to compare the blocks to independent game reads.

A staging tool opens one `StageReadBack` inside its main-thread hop, before its first write. After each write it reads the
thing back from the game and records what the game holds (`Row`). It builds its reply block with `StageReadBack.Reply`
in the same hop. The tool's `success` is false when the block's `ok` is false. The block is named `readBack` on nine tools.
`jawa/set_work_priority` puts the block in `stageReadBack` and keeps the numeric `readBack` for callers that read the
effective priority. Its stage row reads the stored priority from `Pawn_WorkSettings` and faults if the stored value is
unavailable or differs from the requested priority.

It accepts: rows with a wanted value and a value read from the game; a frame number at the open and at the reply; names of
things a clean left; one refusal by name. It does not survive: a tool that passes the request value as the read value (the
wiring checks in the selftest read the call sites for this); a game that changes a thing after the hop.

| promise | test |
|---|---|
| A reply's values are the values read from the game. A row whose read value differs from the wanted value is `ok` false, and the block is `ok` false. | `a_reply_is_built_from_the_read_back_never_the_request` |
| A pawn whose kind the game replaced is reported with the kind as made, and is a staging fault. | `a_replaced_pawn_kind_is_reported_as_made` |
| The block names the frame at the open and at the reply. When the two differ, the block is `ok` false (`frame_moved`). Each of the ten tools opens and replies inside one `InvokeAsync` lambda. | `the_write_and_the_read_back_share_one_frame` |
| A clean that leaves a thing of its filter in its cells names each such thing, and the block is `ok` false. A thing kept on purpose (a pawn, a thing the game cannot destroy) is named as kept and does not make the block false. | `a_clean_that_left_a_thing_names_it` |
| A refusal by name gives `ok` false, the refusal's name, and the rows made before it. A refusal before the first write has no rows. | `a_refusal_by_name_leaves_nothing_made` |
| The block's `digest` is a function of the rows' read values only: thing ids, frames and the row order do not change it. Two builds of one request give equal digests; a different read value gives a different digest. | `two_builds_of_one_request_give_equal_digests` |

## THE STATION ALLOCATOR (`src/RimMandrake/Utils/scene_stations.py`)

Item `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`. Pure Python, no game. It says where on a stage map a scene may
stage (05_build_design.md §Decision 7). The scene library calls it from `s.stage(station=dict(...))`
(`design/specs/2026-11-23-scene-library/boundary.md` §STATIONS). Each promise has a test of its name in
`src/RimMandrake/bridgetools/selftest_stage_stations.py`; the planted faults and their red runs are in
`design/specs/2026-11-23-bridge-v2/live/stage_map/plants.txt`.

It accepts: a stage with its kind (`settlement`, `pocket`, `colony`) and the map's size as read from the game; requests
`size=(w, h)`, `margin`, `edge`, `incident`, `home`, `weather`, `scene`. It does not survive (not promised): a map whose usable
cells are not one rectangle (rock, water: the stage map is bare ground of one terrain); a placement that packs the map best
(the first fit, row by row, is used).

| promise | test |
|---|---|
| No two given or retired stations overlap when each is grown by its own margin. | `no_two_stations_overlap_margins_included` |
| A request that cannot fit is `NO_ROOM`, and the reason names the sizes, the given and the retired counts. | `a_request_that_cannot_fit_says_why` |
| A retired station is never given again, its cells stay taken, and it cannot be released. | `a_retired_station_is_never_given_again` |
| A station given with `edge=n` is at least n cells (plus the edge band) from each map edge; when none fits, `NO_ROOM` names the distance. | `a_station_near_the_edge_is_refused_when_the_plan_asks_distance` |
| A `pocket` stage refuses a request that fires an incident, or needs an edge, a home or weather (`POCKET_CANNOT_SERVE`), and takes nothing. | `a_pocket_stage_refuses_a_scene_that_fires_an_incident` |
| A station on a `colony` stage is marked `shared_map`; on the other kinds it is not. | `a_colony_station_is_marked_shared_map` |
| A released station may be given again; the state written to disk and read back keeps every retirement. | `a_released_station_is_given_again_and_retirement_survives_a_reload` |
| A request or a stage of a wrong shape is refused by name and takes nothing. | `a_bad_request_is_refused_by_name` |

## THE STAGE MAP (`src/RimMandrake/Utils/stage_map.py`)

Item `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS` (05_build_design.md §Decision 7). `stage_map.py make <game> --kind
settlement|pocket` starts from the green room (the one map that the game holds, or a quicktest), feeds it, adds the stage map,
empties it, saves the game as the fixture save `RM_Stage_<game>_<kind>`, and writes the stage file that `s.stage(station=dict(...))`
reads. `register --save NAME` writes a `colony` stage file for a colony save. The live proof is
`src/RimMandrake/bridgetools/prove_stage_map.py`; its last reading is under LIVE READINGS.

It accepts: a game at the menu, or at a map with one map loaded (a game that holds more is left for the menu: a test game is
disposable). It does not survive (not promised): a world with no flat settleable tile within 2000 tile ids of the green room's;
a pocket generator list without MetalHell, Undercave or Labyrinth; an animal that the wild spawner puts on the stage while no
calm holds it (the breach census names it; nothing stops it). Before the empty, `make` reads the stage map back as the current
map and refuses otherwise, because a map switch can reply success and not take (measured 2026-11-24).

| promise | test |
|---|---|
| After make, the stage holds no pawn, and with the calm on it gains none over 60,000 ticks. | `prove_stage_map.py` R1 |
| The green room's colonists are alive, fed and not malnourished after 60,000 ticks of an idle stage. | `prove_stage_map.py` R2 |
| A raid at a settlement stage with cast defenders spawns raiders at an edge with an assault duty. | `prove_stage_map.py` R3 |
| A raid at a stage with no free colonist: the incident journal's outcome (fired, or called and not fired) agrees with the raiders on the stage. | `prove_stage_map.py` R4; offline `selftest_prove_stage_map_rows.py` |
| The make time of each map kind is printed. | `prove_stage_map.py` R5 |
| A pawn on the stage that is not cast is a `BREACH` line on the receipt of `s.stage` and of the close. | `prove_stage_map.py` R6; offline `a_pawn_on_a_station_is_vanished_and_a_pawn_not_cast_is_a_breach` |
