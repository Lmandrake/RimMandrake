# RIMMANDRAKE_ACCEPT_REPIN_BEFORE_GRANT_RECORDED_FIVE_MINUTES_LATE

## spec
`coverage_judge.grant_waits` required the re-pin (a `locked_change`) to come AFTER the `coverage_release_granted`
entry. On Pyrelands, 2026-11-15, the 17-gap fixes and their one re-pin landed at 21:06:06Z and the grant was written at
21:11:14Z, so the chain's release was refused forever ("waits on: the re-pin ... after the grant") and the one look he
granted (OWNER:1794774724955142310) could never apply. A second re-pin would owe a second look. Fix: the re-pin counts
when it comes after the coverage stop the grant lifts (a grant is only ever made on a stop); a re-pin from before that
stop still does not count.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_coverage_judge_loop.py` (new `granted_late` block, 2 checks).
On the base (81fcd3e370) it read FAIL (1): "a re-pin since the stop but before the grant counts" refused naming the
re-pin; the guard check "a re-pin from before the stop does not count" passed. Passes on the fix.
