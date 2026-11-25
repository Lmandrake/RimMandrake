# BOUNDARY: the life cycle of a run, and the run lock (BRIDGE v2.0), Design Version 0.1.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchRunLockCore.cs` (all of it), the lock lines of `Check` in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCompanionSafety.cs`, `TickFin` and the condition run of
`JawaBenchSafeAdvance` in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs`, and the ends of `SceneRun` in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneTickCore.cs`. The run and its trace are on
`../2026-11-23-bridge-v2/boundary.md`; the session is on `../2026-11-23-bridge-v2-hands/boundary.md`.
Item: `RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK`. Each promise has a test of its name in
`src/RimMandrake/bridgetools/selftest_run_life_cycle.py`. The live proof is `src/RimMandrake/bridgetools/prove_run_life_cycle.py`.

## THE LIFE CYCLE

A run ends once, in one state, and then writes its `end`, its last sample and its `close`. At the end, the evaluator is off before
anything else is done, so a fault inside the end cannot leave it armed.

| fault | end |
|---|---|
| a cancel; the driver's lease ended; the session was closed, aborted or taken | `cancelled`, paused |
| the game's own tick threw (no postfix ran: the finalizer `TickFin` speaks) | `threw`, paused; the exception goes on unchanged |
| the evaluator, the arm or the pause threw | `aborted`, with a `threw` fault |
| the game was replaced, or went to the menu | `epoch`; the game that is there now is not touched (`game_replaced`) |
| the run's map left the game | `epoch`, paused |
| a step loop ended for its own reason | `stopped`, `cancelled` or `aborted`, with the loop's reason |
| reading one tick took longer than the caller's `tickBudgetMs` | `budget`, paused; a hit on that tick is a hit |

**The step loops.** `jawa/safe_advance until=` and `jawa/run_scenes until=` arm a run in mode `STEP`. The loop steps the tick, and
stops on the tick where the run ends. For `jawa/safe_advance`, the safety trigger of the same tick is in the run's `triggers`.

**One run at a time.** A run is refused beside a live one (a settling one is live), beside `jawa/safe_advance` and beside
`jawa/run_scenes`. One driver drives a session; the driver of a step run is its own call.

## THE RUN LOCK

From the arm to the `close`, the gate on every `jawa/` tool refuses a call that is not reviewed as a read, by the run's id. A tool
passes when it is on the list `Reads`, or its description begins READ ONLY, or its action is on `ReadActions`, or it is a hand with
its own driver check (`OwnCheck`). A tool that nobody reviewed is a change. `jawa/static_call` is a change, whatever its description says;
the one reviewed call is the read of the process text. An act of the run itself passes. A read is counted, a refused call is named, both on the `close` and on
the reply (`lockReads`, `breaches`).

## LIMITS

- **`tickBudgetMs`: the caller's own, 0 (none) by default.** It guards the caller's clock: a condition over a large rectangle, read
  on every tick, can stop the game from answering. No default, because no such run was measured.
- **75 s for a run of `jawa/run_scenes` to close, then the scene says so** (the writer's 60 s and the 15 s frame stall). Danger: a game
  that draws no frame never closes the run, and the call would never answer.

## DOES NOT SURVIVE (not promised)

- **a-tool-of-the-bridge-host.** The lock is on `jawa/` tools. A `rimworld/` tool has no gate of ours: a load, a speed change or a
  spawn through it is not refused. A load ends the run as `epoch`.
- **a-call-that-was-let-in-before-the-run.** A changing tool that started before the arm and waits inside its body goes on.
- **a-game-that-draws-no-frame.** The `close` is written from a frame. A minimised game that stops drawing closes nothing until it draws.
- **a-killed-game.** The trace on disk has no `close`.
- **a-run-inside-a-plain-step-loop.** `jawa/safe_advance` and `jawa/run_scenes` with no `until` hold no lock: they are no run.

## PROMISES (each one is owed a test of the same name)

- **a-safety-stop-and-a-hit-on-one-tick-report-both.** `triggers` holds both, the state is `stopped`, and `hitTick` is given.
- **the-budget-stop-names-the-costliest-node.** With `tickBudgetMs`, a tick whose reading takes longer ends the run as `budget`; `why` and
  `costliest` name the node or track. With none, nothing stops on cost.
- **an-epoch-change-ends-the-run.** A replaced game, or a map that left, ends the run; another game is never paused by it.
- **two-runs-cannot-be-armed-at-once.** A second run is refused until the first has closed, in a session, alone and in a step loop.
- **a-thrown-tick-still-writes-its-closing-record.** Also when the evaluator, the arm, the pause or the last sample throws.
- **a-changing-tool-during-a-run-is-refused-with-the-run-id.** Every family, and every tool that nobody reviewed.
- **a-read-tool-during-a-run-is-allowed-and-counted.**
- **a-cancelled-run-leaves-the-game-paused.** Nothing of the run is stepped after it. A driver that died: the same, at its lease's end.
- **a-run-refused-for-no-player-control-changes-nothing.** No record, no pause, no request id used up.
- **the-hook-table-check-still-passes.** The finalizer is on `HOOKS.md`.

Later lists beside this page: `polish.md` (none yet).
