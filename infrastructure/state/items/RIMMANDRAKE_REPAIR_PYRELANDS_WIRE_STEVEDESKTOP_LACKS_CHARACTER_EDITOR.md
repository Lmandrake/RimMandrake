# RIMMANDRAKE_REPAIR_PYRELANDS_WIRE_STEVEDESKTOP_LACKS_CHARACTER_EDITOR — SteveDesktop's test list lacks Character Editor

## spec

`selftest_testq_coverage.py` is red: the Pyrelands wire reads `steve_missing: void.charactereditor`.
Cause (classed 2026-11-27): bed2d5c13c put Character Editor on every small tier (owner 2026-11-25:
"Please add Character Editor to all smallmod lists, beside the Zoom requirement."), so the composed
`pyrelands` tier wants it. SteveDesktop gets third-party mods only from
`infrastructure/state/modlists/ModsConfig.MINIMAL.xml` (`sync_test_mods.py`), and that list lacks it.
The probe is right: a Pyrelands job on SteveDesktop would load one mod short of its tier. Fix: put
`void.charactereditor` on the MINIMAL list (beside the zoom mod) and copy it to SteveDesktop with
`sync_test_mods.py --apply --only void.charactereditor`.

## verify

`python3 src/RimMandrake/Utils/testq/selftest_testq_coverage.py` exits 0 with no `FAIL` line; its planted
cases (broken wire H, unreadable hold list) read as before.

## criteria

- The coverage selftest is green on origin/main.
- SteveDesktop's Mods folder holds a mod whose packageId is `void.charactereditor`.

## refs
file: infrastructure/state/modlists/ModsConfig.MINIMAL.xml
file: src/RimMandrake/Utils/testq/coverage.py
