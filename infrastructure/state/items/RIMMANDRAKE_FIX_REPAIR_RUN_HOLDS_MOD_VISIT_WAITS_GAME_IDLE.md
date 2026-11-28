## spec
The Maturation Pipeline tick held FlowWorks's owed in-game visit 14 at 6:15 PM PST 2026-11-27 while ArchBig was free.
`./pipe why FlowWorks` named the live run `rm-detached-bench-rimmandrake-seal-steward-section-blind-j-1795831506`, whose
ticket `RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST` repairs the blind judge's brief (pipeline machinery).
Owed outcome: a run holds a mod's next run only when the run works that mod (its pipeline launched it for one of the
mod's stages on the mod's own work, `mod_work.of`). A run on a ticket that only names the mod, or whose cause is an item
of the mod, does not hold the mod. Two runs never write one mod's files at the same time.

## verify
A selftest, red on the base: a live run on a pipeline repair ticket whose cause is an item of the mod does not stop the
mod's owed visit in a dry tick; a live run that works the mod still stops it; unreadable run records read could-not-look
and launch nothing.

## criteria
- case 1 red on the base, green after; cases 2 and 3 green; a planted "no run holds a mod" fault turns case 2 red.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/Utils/maturation_now.py
