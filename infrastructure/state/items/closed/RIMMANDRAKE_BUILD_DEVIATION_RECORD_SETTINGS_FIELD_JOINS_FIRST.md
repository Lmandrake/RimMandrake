# RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the deviation record of `05_build_design.md` (calm, force, overlay, time and rate; the classes PUT BACK,
  GIVEN BACK and NOT UNDONE with its reach: station, save or process; the stamp; the taint mark and "process dirty"); `jawa/mod_settings_field set` writes only through it; the
  block on `WriteSettings` while a settings entry is live; the journal written before the first poke; the on-screen
  line `OVERLAY <name> <hash>`; the plan's `overlay:` block. This is step 1 of `04_live_tuning.md`.
- **Needs:** the run-plan ticket; the calm profile ticket.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`.

## verify

Acceptance test (offline), 14 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_deviation_record.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_deviation_record.py`, 14 checks: entries applied in
  order, and a failure reverts the earlier ones (1); a failed revert marks the game SPOILED (1); the taint mark stays
  after a revert (1); `overlay: none` with the taint set is not clean (1); a receipt lists every live entry of all four
  kinds with its class (1); a NOT UNDONE entry of reach "save" marks the game state dirty until the fixture is loaded, and one of reach
  "process" stays dirty across a load (2); a
  `const` and a `static readonly` target are refused by name (2); an overlay entry is refused with a canonical save loaded (1); a second
  holder cannot apply (1); the journal exists before the first write (1); a settings write to disk is blocked while an
  entry is live (1); a value changed by another hand is listed as differing from its default (1).

- **Live test (UNRUN):** `python.exe src\RimMandrake\bridgetools\prove_overlay_settings.py`: experiments E1 and E2
  of `04_live_tuning.md`.

Live state at filing: UNRUN: its script `prove_overlay_settings.py` does not exist yet.

## criteria

- The acceptance test prints 14 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
