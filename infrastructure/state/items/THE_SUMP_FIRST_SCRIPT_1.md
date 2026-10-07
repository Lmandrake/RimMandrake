# THE_SUMP_FIRST_SCRIPT_1

Child of NORTHSTAR_EVERYWHERE_PROGRAM_1. Process: `design/RimMandrake/debug_process.md` (being written; the owner's rulings are on the parent).

## spec
First north-star script for **TheSump** (`src/RimMandrake/TheSump/`): a `validation.py` + driver plan centred on the mod's INTENDED function. Read its `About/About.xml`, its defs and any design doc under `design/` to list what the mod is meant to do; one bar per intended behaviour, each with a cheap state check through the bridge (the checks must be able to FAIL: prove each against a deliberately broken or absent case). Also add the debugging checks already known to be useful for this mod (open items, past bugs). Template and live harness: Graffiti and Pyrelands (`src/RimMandrake/Graffiti/`, `src/RimMandrake/Pyrelands/`), driver `src/RimMandrake/Utils/northstar_driver/`. Static-lint every bridge call against the declared tool schemas. Agents may approve their own scripts (owner, 2026-10-01).

## verify
Run live via `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod TheSump --plan <plan>` on the smallest tier that loads the mod; results JSON in `Transient/northstar/`. Each non-pass is classified harness / site / mod / unmeasured. Mod defects found are filed or fixed (bug fixes are allowed during the pause).

## criteria
- A1 L0: modcheck floor shows every bar of TheSump covered
- A2 L1: every def parsed from TheSump's Defs/ resolves live via jawa/get_defs (81 defs, none held: the DEPLOY_HOLD lift of 2026-10-03 left 0 TheSump holds), so defs_resolve is measured and held_defs_are_unmeasured_by_hold reports nothing
- A3 GREEN-MIN: one live northstar_driver run of TheSump is recorded with its results JSON
- A4 GREEN-MIN: every FAIL in the TheSump run is classified as harness, site, mod or unmeasured

The manifest at `df8e3b7f3` said A2 was "the 35 DEPLOY_HOLD held defs are resolved". That was stale: every TheSump
hold was lifted 2026-10-03 (`8cacbb66c`), and `validation.py` measures `HELD_DEFS` = 0 and `SHIPPED` = 81.
