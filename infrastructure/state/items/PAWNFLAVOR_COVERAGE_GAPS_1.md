# PAWNFLAVOR_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `PawnFlavor` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The PawnFlavor `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
9 of 11 faction filter patches (all RUT_Jawa_* factions) unverified live (needs mandrake.rut.patches); pirate-leak containment (Blackstar not reaching Junkers); Pirate pawn draw; any trait actually doing something; About.xml count stale (50/5 vs 77/13)

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
