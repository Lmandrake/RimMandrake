## spec
Codex claim 8 of RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED (review raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), verified by a red case.
`condition` with an unreadable store skips the unit (exit 2) and leaves the run admitted; `ended` moved only `started` runs, so the run stayed admitted after its unit ended (reconcile runs only from `pipe doctor`). Fix: `ended` on an admitted run marks it refused (it never ran its payload: NEVER_RAN, so its name may be admitted again), its reservations released as a system fault.
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` must print no `FAIL claim 8:` line
(t_review_claims_eight). Watched red on base f9ebc4f931 (2026-11-18 ~5:40 PM PST) [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- selftest_control's `claim 8` checks pass; the whole selftest passes.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
