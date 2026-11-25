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

Not yet in the trace, each with its ticket in `06_build_order.md`: the tap records with their two sequence numbers; the alias
links; the plan and checker versions; the reviewed list of readers (a track may read a property today).

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

## LIVE READINGS

| proof | reading | evidence |
|---|---|---|
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
