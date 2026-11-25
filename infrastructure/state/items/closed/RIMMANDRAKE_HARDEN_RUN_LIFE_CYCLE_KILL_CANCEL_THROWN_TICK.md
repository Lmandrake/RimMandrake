# RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the run's life cycle under faults: the run lock (while a run is live, the gate on every tool refuses the
  changing families, by the run's id; reads are counted); one driver per run; a clean end on cancel, on a thrown tick,
  on a changed game or map, on a driver that died; the same per-tick evaluator in the two step loops
  (`jawa/run_scenes`, `jawa/safe_advance`) with their exact stop; the epoch check; the refusal to start when the
  player has no control.
- **Needs:** the slice.

Depends on: `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`.

## verify

Acceptance test (offline), 10 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_run_life_cycle.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_run_life_cycle.py`, 10 checks: a safety stop and a
  hit on one tick report both; the budget stop names the costliest node; an epoch change ends the run; two runs cannot
  be armed at once; a run that ends on a thrown tick still writes its closing record; a changing tool called during a
  run is refused with the run's id; a read tool called during a run is allowed and counted; a cancelled run leaves the
  game paused; a run refused for "no player control" changes nothing; the hook table check still passes.

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_run_life_cycle.py`, 4 rows: the driver
  killed in the middle leaves a closing record and a paused game; `jawa/spawn_pawn` from a second caller during a run
  is refused and is a breach on the receipt; the STEP loops stop on the exact tick; a thing spawned and destroyed
  inside one tick is in the trace by its taps.

Live state at filing: UNRUN: its script `prove_run_life_cycle.py` does not exist yet.

## criteria

- The acceptance test prints 10 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a run lock that covers `jawa/` tools of one family only; a cancel that leaves the
  evaluator armed.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
