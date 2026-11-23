# RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the full stage phase: terrain, structures with stuff and health, things with counts, a pawn with exact
  kind, faction, health (each injury and part), gear, skills, traits, work types, needs, position, facing; every
  write read back from the game; fixtures by name; clean with read-back.
- **Needs:** the run-plan ticket.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.

## verify

Acceptance test (offline), 10 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_ops.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_ops.py`, 10 checks on the pure plan-to-ops
  layer: each op's refusal by name (6); a reply is built from the read-back, never from the request (1); a pawn whose
  kind was replaced by the game is a staging fault (1); two builds of one plan give equal digests on recorded
  read-backs (1); a clean that left a thing behind names it (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_stage_ops.py`, 5 rows: a 400-cell station
  with 10 pawns is cleaned and built, and the time is printed; the same plan built twice gives equal read-back
  digests; a spawn that the game answered with another kind is reported; a scene run after a deliberately dirty scene
  (corpses, a reservation, a fire) gives the result of a fresh station; a station that cannot be cleaned is retired.

Live state at filing: UNRUN: its script `prove_stage_ops.py` does not exist yet.

## criteria

- The acceptance test prints 10 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a reply that echoes the request; a clean that reports success with a corpse left.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
