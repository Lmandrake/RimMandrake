# RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `design/specs/2026-11-23-bridge-v2/boundary.md` (the trace schema and the evidence contract of
  `05_build_design.md`). In `JawaBenchVitals.cs` `TickPost`, an optional per-run evaluator for **PLAY only**: the fixed
  order (sample, conditions, end test, act steps), `CondRun.Step` after every tick, tracks written on change through
  `JawaBenchTpsWriter.Enqueue` as kind `scene`, the first and last samples, sequence numbers and phases, the random
  state compared round the sample phase, the closing record after the writer drained, the pause in the postfix read
  back. One hand-written scene: one probe on one pawn, one act (a damage), one end condition. Closes the intent of
  `ADVANCEUNTIL_WIRE_PER_TICK_STOP`.
- **Needs:** nothing.

Depends on: nothing.

## verify

Acceptance test (offline), 11 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py`, 11 checks on a .NET harness
  that compiles the pure files (the pattern of `SceneRunnerSelfTest`): a hit on tick T gives `executed == T`; true at
  arm gives `executed == 0`; a track writes one row per change and none without a change; a probe that goes `gone`
  writes `gone`, never 0; an unknown under `on_unknown: stop` ends the run as unknown; a skipped original records
  nothing; a dropped row is counted in the closing record; **inside one tick the sample record's sequence number is
  lower than the act record's**; an act step and the end cannot fall on one tick; the first and the last sample exist
  for every track; a random draw inside the sample phase is reported.

- **Live test (UNRUN until a game is held):** `python.exe src\RimMandrake\bridgetools\prove_scene_tick_wiring.py`,
  5 rows: `until(game.tick >= T0+137)` gives `hitTick == T0+137` at speed 1 and at Ultrafast, with the game paused on
  that tick and the tick count read after the frame ended; a private field path reads the same value as
  `jawa/pawn_get`; an actor damaged by the act step shows the new health in the trace before the run ends; the trace's
  closing record counts zero dropped rows; steady-state allocation is 0 (`jawa/alloc_probe`).

Live state at filing: UNRUN: its script `prove_scene_tick_wiring.py` does not exist yet.

## criteria

- The acceptance test prints 11 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** sampling after the act steps (caught by the sequence check); a closing record
  written before the writer drained; a stop that lets one more tick run.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
