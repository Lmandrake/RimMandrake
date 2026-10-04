# LORESTAGES_COVERAGE_GAPS_1

Child of NORTHSTAR_COVERAGE_AUDIT_1. Row `LoreStages` of `design/RimMandrake/northstar_coverage_audit_2026-10-03.md`.

## spec
The LoreStages `validation.py` asserts little of what the mod does. Uncovered, per the audit (a Sonnet reader's evidence; re-read the mod first):
(1) The one mechanism, stage N rewrites description/label/settleWarning and rung-down restores, is UNMEASURED live (no bridge tool reaches SetStage; only offline Source/SelfTest exe covers it, not wired into the suite); (2) master toggle off -> stage-0 text unasserted; (3) scribe/save-load of stage per ladder unasserted

Add a component per uncovered behaviour that asserts it DOES its job (not spawn-and-count), one per settings toggle with an off arm. Static/offline bars first.

## criteria
Each listed behaviour has an asserting component or a stated reason it cannot (UNMEASURED with the missing instrument named); `lint_calls.py` clean for the file.
