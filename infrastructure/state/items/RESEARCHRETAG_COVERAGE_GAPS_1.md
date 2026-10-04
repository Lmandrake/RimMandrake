# RESEARCHRETAG_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `ResearchRetag` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The ResearchRetag `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
~264 of 269 retag rows and ~400 tab assignments (donor mods absent); RUT_Ported_ResearchTrio 18 native ResearchProjectDefs (zero refs in script); GravForge building + recipes; prerequisite cycle/dangling-prereq check; load-order forceLoadAfter

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
