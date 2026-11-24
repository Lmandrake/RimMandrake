# RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH

One ticket of the Bridge v2.0 build order, under the enacted pick of pass three. Read
`design/specs/2026-11-23-bridge-v2/11_design.md`, then the contract pages it names in
`design/specs/2026-11-23-bridge-v2/contracts/`. The order is the last section of
`design/specs/2026-11-23-bridge-v2/06_build_order.md`. Filed by `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`.

## spec

The instruments: the exact stop, the per-tick recorder, the hidden read, the act batch. C#, generic, no scene and no
verdict in them. Contracts served: `contracts/run.md`, `contracts/read.md`, `contracts/act.md` (the batch and the
request ids), `contracts/attach.md` (the session's state).

- **Builds:** `jawa/run_until` from `jawa/scene_slice` (landed offline, `5cebf3567fe1`): any condition tree; tracks on
  any value path of any bound thing or frozen group, on every tick, written on change; no pawn argument and no built-in
  act; the first evaluation before any tick; an unreadable value of the condition ends the run as `unknown`; a request
  id given by the caller, with a status by id.
- `session` actions open, state, close and abort, so that one trace and one run lock span several runs.
- `jawa/read_paths`: a read-only read of many value paths in one call on one tick: public and private fields, statics
  of a mod, def values, comps by class, properties from a reviewed list only; each value with its state (`ok`, `gone`,
  `unbound`, `error` with the fields that the type has). The recorder and this read share one path evaluator.
- `jawa/act_batch`: a list of acts (a present tool's name and its arguments, each with a request id) done in order in
  one main-thread hop; one reply per act; a start and an end record per act in the trace with the tick and the frame
  count; a repeat of an id with the same arguments returns the first reply; with other arguments it is refused. If the
  present tool bodies cannot be called inside one hop without a rewrite, the ticket says so with the count and stops
  there.
- Each new hand is a plain public static method with a thin tool wrapper (`11_design.md`, "What serves Inhabited").
- `jawa/scene_slice` keeps working until its proof script converts.

## verify

Acceptance test (offline), 18 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_run_until.py
```

Seen red on base `47689bd93d` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** 18 checks on the C# core through the offline harness: the eleven promises of `boundary.md` still
  pass with no act step (1); two runs of one session write one trace with no gap in `n` (1); a condition that is true
  at the start ends as hit with no tick played (1); a hit and the limit on one tick end as hit (1); an unreadable value
  of the condition ends the run as `unknown` on that tick and names the value (1); a dead member of a frozen group is
  recorded `gone` and stays in the group, and a later spawn is not in it (1); a track on a private field and on a
  static field reads the value (1); a path with a wrong field name is `error` with the type's fields (1); a path that
  calls a method that is not on the reviewed list is refused by name (1); 1,000 reads leave the state digest equal
  (1); a caller that is not the session's driver is refused while the session is open, and the driver is allowed (1); a
  session past its lease is not closed by itself, can be read, and the game is paused (1); a run started with no open
  session is refused by name (1); `scene_slice` still passes its own selftest (1); a batch of two acts writes no frame
  count change between them (1); a repeated request id with the same arguments returns the first reply and does
  nothing (1); with other arguments it is refused (1); a batch whose second act throws reports the first as done and
  the second as failed (1).
- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_run_until.py` (the stop tick is read a second
  time by `TicksGame` after the pause and equals the trace's tick; the count of trace rows equals the closing record's
  count; a private field of a FlowWorks comp is recorded on every tick of 200) and
  `python.exe src\RimMandrake\bridgetools\prove_act_batch.py` (a per-frame counter that the batch does not write is
  equal before and after a batch of two acts; a repeated damage request leaves the victim's health as after one hit).
  Then experiment A: `python.exe design\specs\2026-11-23-bridge-v2\experiments\exp_a_python_act_vs_kernel_act.py --trials 10`.

Live state at filing: UNRUN: the two proof scripts do not exist yet.

## criteria

- The acceptance test prints 18 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a second run that starts a new trace; an unreadable condition value counted as false;
  a group that drops its dead member; a read that returns 0 for a gone thing; a batch that hops once per act; a repeated
  id that is done twice; a run lock that refuses the session's own driver.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on a
  boundary page first (`design/specs/2026-11-23-bridge-v2/boundary.md`, or the contract page of the name it serves).
