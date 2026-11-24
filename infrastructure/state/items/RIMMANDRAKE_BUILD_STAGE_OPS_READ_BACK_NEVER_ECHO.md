# RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

**Split by pass three (2026-11-23, `design/specs/2026-11-23-bridge-v2/11_design.md`).** The Python part of this ticket
is no longer here: the stage phase is `s.stage` (`contracts/stage.md`), built by
`RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP` when its first scene needs it. This ticket keeps the C# duty only.

- **Builds (C# only):** each staging tool that `s.stage` calls (`jawa/build_batch`, `jawa/set_terrain_batch`,
  `jawa/spawn_pawn`, `jawa/destroy_batch`, the pawn kit tools) replies from a read-back that is made **in the same
  main-thread hop** as the write, so that no frame runs between making a thing and checking it; a clean with
  read-back that names what it left.
- **Needs:** the instruments ticket (one companion build at a time).

Depends on: `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH`.

## verify

Acceptance test (offline), 6 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_ops.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test (pass three):** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_stage_ops.py`, 6 checks on the C# reply
  builders through the offline harness: a reply is built from the read-back, never from the request (1); a pawn whose
  kind was replaced by the game is reported with the kind as made (1); the frame count at the write equals the frame
  count at the read-back, for each of the four batch tools (1); a clean that left a thing behind names it (1); a tool's
  refusal by name leaves nothing made (1); two builds of one request give equal read-back digests on recorded replies (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_stage_ops.py`, 5 rows: a 400-cell station
  with 10 pawns is cleaned and built, and the time is printed; the same plan built twice gives equal read-back
  digests; a spawn that the game answered with another kind is reported; a scene run after a deliberately dirty scene
  (corpses, a reservation, a fire) gives the result of a fresh station; a station that cannot be cleaned is retired.

Live state at filing: UNRUN: its script `prove_stage_ops.py` does not exist yet.

## criteria

- The acceptance test prints 6 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a reply that echoes the request; a clean that reports success with a corpse left.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
