## spec
Codex claim 1 of RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED (review raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), verified by a red case.
`_cgroup_pids` turned a failed `systemctl show` (rc != 0: bus down, timeout) into `([], "")`, the shape of an empty cgroup, so `kill_units` said "nothing was running in it" and `stop --kill` recorded the run killed and returned its clone though nothing was verified. Fix: a failed read returns None with its cause, so the kill reads death UNVERIFIED and is not recorded killed. (`systemctl show` on a unit that does not exist exits 0 with an empty value [measured], so only a real failure changes.)
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` must print no `FAIL claim 1:` line
(t_review_claims_eight). Watched red on base f9ebc4f931 (2026-11-18 ~5:40 PM PST) [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- selftest_control's `claim 1` checks pass; the whole selftest passes.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
