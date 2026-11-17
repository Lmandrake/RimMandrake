## spec
`refusal_contract.py calibrate --no-run` reads coverage_judge UNTESTED (2026-11-16 8:50 PM PST) while
infrastructure/state/judge_calibration.json records it CALIBRATED: its brief was edited after calibration, so every coverage
refusal is advisory (the Designer is not sent back) until it is recalibrated. Found because
selftest_bar_rule_tuning_numbers.py's later-look case read the live registry and went red at publish; that case is now hermetic
(249d1ee36f), the live state is not fixed. Which edit reset it is unmeasured.

## verify
Acceptance test: python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run | grep coverage_judge prints CALIBRATED; today UNTESTED.

## criteria
- coverage_judge reads CALIBRATED at its current brief, by its planted cases, not by hand.

## refs
file: infrastructure/state/judge_calibration.json
file: src/RimMandrake/rimflow/refusal_contract.py
