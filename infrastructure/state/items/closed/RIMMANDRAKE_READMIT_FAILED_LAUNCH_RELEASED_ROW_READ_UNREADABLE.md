## spec
Codex claim 5 of RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED (review raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), verified by a red case.
`_mark(..., 'fail_launch')` releases the run's reservations; re-admission deleted only held ones, so the released rows kept their UNIQUE (run, mod, resource, win) key, the new INSERT raised IntegrityError and the retry read as CONTROL UNREADABLE. Fix: re-admission under a name that never ran deletes the run's held and released rows.
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` must print no `FAIL claim 5:` line
(t_review_claims_eight). Watched red on base f9ebc4f931 (2026-11-18 ~5:40 PM PST) [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- selftest_control's `claim 5` checks pass; the whole selftest passes.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
