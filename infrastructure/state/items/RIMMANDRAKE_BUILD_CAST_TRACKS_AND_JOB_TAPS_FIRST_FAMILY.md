# RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the standard cast tracks (position, facing, job, toil, health summary, downed, dead, mental state,
  carried thing, holder, faction, drafted); the taps for job start and end (with who gave the job and the end
  condition) and for a reservation made and refused.
- **Needs:** the run-plan ticket.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.

## verify

Acceptance test (offline), 9 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_cast_tracks.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_cast_tracks.py`, 9 checks on the pure recorder: the
  six hook rules of `HOOKS.md` for each of the two taps (2); two job starts in one tick keep their order (1); a record
  outside any run is dropped and counted (1); an alias whose object is replaced writes a link record (1); a track on a
  replaced job re-binds (1); the settle reconciliation catches a death with no kill record (1); the hook table check
  passes (1); the per-tick cost of the tracks is in the result (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 9 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a job tap that records the new job only; an alias that silently moves to a corpse.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
