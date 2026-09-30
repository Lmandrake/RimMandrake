# MOEVENTS_FINDMOD_RETIRED_1

`selftest_retired_mods.py` fails (caught 2026-09-29, first seen in a pre-commit
full run; unrelated to the change being committed): two patch files carry
`PatchOperationFindMod` blocks naming the retired mod **Mo'Events (Continued)**:

- `src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml`
- `src/RimUtinni/UtinniPatches/Patches/MoEventsAbomination_YuuzhanVongRename.xml`

A FindMod on an absent mod returns true-on-no-match silently, so these blocks are
dead weight at best. Fix is to remove or re-target the two blocks per whatever
retired Mo'Events' content — check `CANON_DRAIN_1` (mentions the Mo'Events cut in
passing) and the retired-mods list the selftest reads, then rerun
`python3 src/RimMandrake/Utils/selftest_retired_mods.py` to green.

NEXT: delete or re-target the two FindMod blocks, selftest green, close with the
fix's sha.
