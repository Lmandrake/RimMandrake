## spec
DESIGN DECISION 2026-11-18 (on RIMMANDRAKE_AUDIT_FOREIGN_DEF_ROWS_FAIL_IN_THREE_MODS, which this item replaces): not an Auditor rule (the Auditor role is switched off in dispatcher_schedule.json). The rule lives in the shared validation core as one pure function a live row asks when `get_defs` reports a def `notFound`:
`validation_core.missing_def_verdict(owner, own, active) -> (status, class, detail)`; the three answers are in the acceptance test's header. A mod that is not loaded is "could not look", never the asking mod's defect.
- Use it in the four rows the finding names: CreatureBehaviors (`RSW_Ollopom`, validation.py:489), UtinniPatches (`RSW_Zersium`, `RSW_Phrik`), Atlas (`RUT_Rites_ScrapShrine`, `_expect_lit`), each declaring the def's owner packageId.
- `infrastructure/state/facts/instrument_traps.md` line 205 gains the function's name.
- Live part: UNRUN. The three mods are not in the Maturation Pipeline and the nightly is held; the rows' live readings are owed to the next run of each suite: `python3 src/RimMandrake/Utils/modcheck.py run <Mod>` is NOT to be used for it (it rewrites ModsConfig); the suite's own testq job is.

## refs
file: src/RimMandrake/Utils/validation_core.py
file: src/RimMandrake/CreatureBehaviors/validation.py
file: src/RimMandrake/Atlas/validation.py

## criteria
- The acceptance test passes 13 of 13; the four named rows call the function; selftests of validation_core stay green.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/foreign_def_not_found_accept.py` (13 checks; on 0dc24342c3 in a throwaway `git clone --shared`, watched: 13 red). Covers: owner not loaded, owner loaded, no owner, owner is the asker, list unread, list empty but read, case differences both ways, a different foreign owner, a blank owner, a list of the wrong type.
