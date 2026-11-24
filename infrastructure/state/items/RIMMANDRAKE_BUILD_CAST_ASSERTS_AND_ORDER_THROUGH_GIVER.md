# RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

**Split by pass three (2026-11-23, `design/specs/2026-11-23-bridge-v2/11_design.md`).** The Python part of this ticket
is no longer here: the capability asserts are reads (`can=` of `s.stage`, `s.read`), and
the order is the verb `s.act.order` (`contracts/act.md`); each is built by the ticket whose scene first needs it. This ticket keeps the C# duty only.

- **Builds (C# only):** the order through the game's own giver code, on the body of `jawa/ordered_job`, with the
  giver's refusal returned as a fact and the giver's name on the job tap's "given by" field; the motive act (a lord and
  a duty, from the `jawa/lord_*` bodies); the force level of each actor on the deviation record. Python never copies a
  giver's rules.
- **Needs:** the stage map ticket; the cast tracks ticket.

Depends on: `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`, `RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY`.

## verify

Acceptance test (offline), 4 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_force.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test (pass three):** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_force.py`, 4 checks on the C# core:
  an order declared "through the giver" that the giver refuses returns `given=False` with the giver's reason, and starts
  no job (1); the force level written to the record is the level that was used, not the level that was asked (1); a
  motive for a pawn with no lord is refused by name (1); a raw job is recorded as raw (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_ordered_rescue.py`, 5 rows: the rescue
  completes (SUCCESS); a rescuer whose work type is disabled fails its assert before a tick is spent; a hostile with no
  lord is refused at stage with the reason; **the force level on the receipt is checked against the game**: for an
  order declared "through the giver", the job tap's "given by" field names that giver, and for a raw order it does
  not; a giver made to refuse gives MOD FAILURE.

Live state at filing: UNRUN: its script `prove_ordered_rescue.py` does not exist yet.

## criteria

- The acceptance test prints 4 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red (live):** an executor that always starts a raw job and copies the declared level onto
  the receipt. GPT named this: the offline checks of my first draft would have passed it.
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
