## spec
`python3 src/RimMandrake/Utils/testq/selftest_stage6_checks.py` is red on origin/main (seen on 8fd0277b24 by ./publish,
2026-11-27): `the-four-mods-are-takeable: Pyrelands (before blind): 41 takeable, 38 blocks committed, each block a check
whose tier fits`. The one block outside the fitting checks is `sc_ullai`. Its placement reads `could not look`: "no
program reads a verdict of this check from src/RimMandrake/Pyrelands/validation.py (entry herd_follows_drive)". The
table moved sc_ullai to the chain `ullai_and_giant` (note on RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START);
the row or its committed block still names the old entry. Repair the row or the block so that sc_ullai is takeable, or
its block goes. Do not move a bar.

## refs
file: design/concepts/Pyrelands/version/test_table.json
file: src/RimMandrake/Pyrelands/validation.py

## verify
`python3 src/RimMandrake/Utils/testq/selftest_stage6_checks.py` exits 0.

## criteria
The selftest passes; sc_ullai is placed takeable with its block, or has no block.
