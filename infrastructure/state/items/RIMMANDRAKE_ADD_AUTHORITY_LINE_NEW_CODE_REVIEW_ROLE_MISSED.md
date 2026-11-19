# RIMMANDRAKE_ADD_AUTHORITY_LINE_NEW_CODE_REVIEW_ROLE_MISSED

## spec

`src/RimMandrake/rimflow/roles/code_review.md` (added by the code-review calibration lane, last at `c89dea59f0`) does not
name `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, and `src/RimMandrake/rimflow/selftest_conductor_authority.py` requires
every role and agent file to (measured 2026-11-19 BENCH: "FAIL src/RimMandrake/rimflow/roles/code_review.md names the
ruling", 1 failure; red on origin as well, so not caused by the era work). Do: add the one standard authority line the
other role files carry, in the lane that owns the file (it was being calibrated the same day).

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    python3 src/RimMandrake/rimflow/selftest_conductor_authority.py

ends with 0 failures once done. Watched failing 2026-11-19 BENCH at `ed3b6ca7a5` and `fbdf50a5b2`: 1 failure.

## criteria

- A1: every role and agent file names the ruling (the selftest above is green).

## refs

file: src/RimMandrake/rimflow/roles/code_review.md
