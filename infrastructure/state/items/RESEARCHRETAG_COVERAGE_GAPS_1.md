# RESEARCHRETAG_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `ResearchRetag` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The ResearchRetag `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
~264 of 269 retag rows and ~400 tab assignments (donor mods absent); RUT_Ported_ResearchTrio 18 native ResearchProjectDefs (zero refs in script); GravForge building + recipes; prerequisite cycle/dangling-prereq check; load-order forceLoadAfter

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.

## progress 2026-10-03 (r34)
- Static-free readback wired: `every_shipped_def_reads_back` (shared shipped_defs) covers all 46 shipped defs incl. the 18 ported ResearchProjectDefs and GravForge (loaded + label). baseCost/tab are not compared: this mod retags them on purpose. Still open: the ~264 donor retag rows, prereq cycle/dangling check, forceLoadAfter.
