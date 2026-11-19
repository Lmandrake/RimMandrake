## spec
Codex claim 2 of RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED (review raw:
`D:\ClaudeWork\scratch\control_hooks_review_20261118\codex.txt`), verified by a red case.
With the store unreadable (or no run row for the unit), `pipe stop <unit> --kill` built a stand-in row with spec "{}" and lost the run's `extra_units`: its claude scope `claude-seat-<seat>-<unit>.scope` (role_launch.role_scope; detached_helper.scope_name), a separate cgroup the service kill does not reach. Fix: the stand-in row lists `claude-seat-*-<unit>.scope` from systemd; a listing that fails leaves the kill UNVERIFIED, never ok.
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_control.py` must print no `FAIL claim 2:` line
(t_review_claims_eight). Watched red on base f9ebc4f931 (2026-11-18 ~5:40 PM PST) [measured].

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- selftest_control's `claim 2` checks pass; the whole selftest passes.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_control
