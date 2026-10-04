# PAWNFLAVOR_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `PawnFlavor` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The PawnFlavor `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
9 of 11 faction filter patches (all RUT_Jawa_* factions) unverified live (needs mandrake.rut.patches); pirate-leak containment (Blackstar not reaching Junkers); Pirate pawn draw; any trait actually doing something; About.xml count stale (50/5 vs 77/13)

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.

## progress 2026-10-03 (r34)
- `every_shipped_def_reads_back` wired (77 backstories by title/titleShort/slot, 13 traits loaded). About.xml count corrected (was 50/5 + "droid backstories absent"; measured 77 = 30 childhood + 47 adulthood across 13 faction categories, 13 traits, FDE droid sets present). Still open: faction filters live, pirate-leak containment, traits doing anything.
