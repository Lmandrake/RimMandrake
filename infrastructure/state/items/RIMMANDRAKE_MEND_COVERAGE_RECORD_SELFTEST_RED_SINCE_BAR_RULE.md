# RIMMANDRAKE_MEND_COVERAGE_RECORD_SELFTEST_RED_SINCE_BAR_RULE

Found 2026-11-16 by the steward run RIMMANDRAKE_STEWARD_LEANINGSCRUB_PREFLIGHT_STAGE, when ./publish ran the pipeline checks for a change to `src/RimMandrake/rimflow/maturation.py` and refused on this test. Measured red on an export of origin/main at 2626f90d0b (no local change in it), so it is not caused by that change.

## spec
`python3 src/RimMandrake/rimflow/selftest_coverage_refusal_record.py` fails one case:
`FAIL bad row fixed on re-ask: both refusals stand, the contract accepts the whole look  got: ('not_covered', None, [['leaf_wall'], ['inv_throw']])`.
Guess (not measured): the case's `inv_throw` gap ("the throw scene reads no distance") may now be read by the bar rule of 579eb06168 (coverage judge: a passing bar is an experience, never a tuning number) so the contract field comes back None. Find whether the code or the case is wrong; a weakened assertion is not a fix.

## criteria
- The case passes for a reason the test states; no assertion weakened, skipped or deleted.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_coverage_refusal_record.py` ends `PASS` with 0 failures. Watched failing 2026-11-16 on origin/main 2626f90d0b: `FAIL (1)`.

## refs
file: src/RimMandrake/rimflow/selftest_coverage_refusal_record.py
file: src/RimMandrake/rimflow/coverage_judge.py
