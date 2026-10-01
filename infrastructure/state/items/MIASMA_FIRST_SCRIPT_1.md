# MIASMA_FIRST_SCRIPT_1

Child of NORTHSTAR_EVERYWHERE_PROGRAM_1. Process: `design/RimMandrake/debug_process.md` (being written; the owner's rulings are on the parent).

## spec
First north-star script for **Miasma** (`src/RimMandrake/Miasma/`): a `validation.py` + driver plan centred on the mod's INTENDED function. Read its `About/About.xml`, its defs and any design doc under `design/` to list what the mod is meant to do; one bar per intended behaviour, each with a cheap state check through the bridge (the checks must be able to FAIL: prove each against a deliberately broken or absent case). Also add the debugging checks already known to be useful for this mod (open items, past bugs). Template and live harness: Graffiti and Pyrelands (`src/RimMandrake/Graffiti/`, `src/RimMandrake/Pyrelands/`), driver `src/RimMandrake/Utils/northstar_driver/`. Static-lint every bridge call against the declared tool schemas. Agents may approve their own scripts (owner, 2026-10-01).

## verify
Run live via `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Miasma --plan <plan>` on the smallest tier that loads the mod; results JSON in `Transient/northstar/`. Each non-pass is classified harness / site / mod / unmeasured. Mod defects found are filed or fixed (bug fixes are allowed during the pause).

## criteria
`modcheck floor` shows every bar covered; one live run recorded with its results JSON; every FAIL is a classified finding, not hidden; script committed with explicit paths.
