## spec
Codex claim 3 of RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED (review raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), verified by a red case.
A stop aimed at a unit (`pipe stop rm-... --kill|--write-now|--at-easy-spot`) skipped `_cancel_in_scope`, and `_live_runs` reads only `started`, so an admitted (not yet started) run kept its admission: its unit's ExecCondition still passed after the stop said done. Fix: the unit-targeted stop cancels the unit's admitted run in the same transaction (reservations released).
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` must print no `FAIL claim 3:` line
(t_review_claims_eight). Watched red on base f9ebc4f931 (2026-11-18 ~5:40 PM PST) [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- selftest_control's `claim 3` checks pass; the whole selftest passes.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
