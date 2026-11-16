# RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS

## spec
A `covered` verdict signs under an UNTESTED brief (calibration is read only on `not_covered`); `calibrate` promotes on
free_check exit 0 and always writes the registry (`--no-run` too); submit raises repair_due and alarms before reading
calibration; judge_calibration.json says FlowWorks was signed by the coverage judge, tree.json says Arbiter. Source:
skeptical review 2026-11-15 (`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\claims_checked.md`
B7, B8, B10, C8; `design/RimMandrake/maturation_pipeline.md` §9 item 12; lesson
20261115T132719Z-BENCH-calibrate-no-run-writes-registry).

## decision (2026-11-15, Evidence-for-Ask, delegated)
Taken under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME (no evidence against the obvious answer).

1. Symmetric: a judge brief signs either verdict (`covered` or `not_covered`) only when CALIBRATED; under an UNTESTED
   brief both are advisory.
2. `calibrate` checks that its planted cases actually ran and came out as planted, not just that free_check exited 0.
3. `calibrate --no-run` writes nothing (read-only status).
4. An advisory (uncalibrated) refusal raises no repair and no alarm.
5. Not retroactive: signatures already made under an UNTESTED brief are flagged in the status output, not voided.
6. Fix the signer mismatch (judge_calibration.json vs tree.json) so one record names who signed.

Sequencing (measured 2026-11-15: judge_calibration.json has coverage_judge UNTESTED, only evidence_gate CALIBRATED):
the builder calibrates coverage_judge with planted cases both ways FIRST, in the same item, or the exam + coverage
judge passes owed for GimmeSomeSlack and Pyrelands (his card 2026-11-15 05:36Z) would stall on advisory verdicts.

Sources: his card 2026-11-14 19:22Z "Do the Exam and coverage judge stay as gates before a lock? (spec Q7) -> Keep
both" (a gate is only a gate if its judge is trustworthy in both directions). Evidence against: none found.

Builder also owes: update `design/RimMandrake/maturation_pipeline.md` §9 item 12 and the spec's Q7 mark.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_judge_calibration.py
src/RimMandrake/rimflow/selftest_refusal_contract.py`, new cases: covered under UNTESTED does not sign; calibrate with
a case that did not run stays UNTESTED; --no-run leaves the registry bytes unchanged; advisory refusal raises no repair.
