## spec
Codex claim 6 of RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED (review raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), verified by a red case.
`escalate` took the newest pending stop order of the unit without reading its deadline: a timer for an older write-now order marked a newer deadline-free order escalated and wrote that its deadline passed, and a timer firing before any deadline still killed. Fix: escalate picks the newest pending order whose deadline has passed (2 s slack) and kills nothing when none has.
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` must print no `FAIL claim 6:` line
(t_review_claims_eight). Watched red on base f9ebc4f931 (2026-11-18 ~5:40 PM PST) [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- selftest_control's `claim 6` checks pass; the whole selftest passes.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
