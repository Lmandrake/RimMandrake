## spec
`selftest_control.py` launches real user-systemd units under fixed names (`rm-probe-race-b`, `rm-probe-kill1`, `rm-probe-crash2`, about 40 more). Two runs at once (sibling clones publishing, each `./publish` runs it) share one user systemd, so one run's unit is "already loaded" for the other, or one run's `pipe stop --kill` kills the other's unit. Seen 2026-11-19: `./publish` refused for RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST on "the trap fixture starts", and two runs started together failed 3 checks each ("Unit rm-probe-race-b.service was already loaded"), base 50bd2f576 plus that item's edits.
Fix: the selftest's main() takes an exclusive flock on one per-user lock file, so runs on one machine take turns.
Acceptance test: `cd src/RimMandrake/rimflow; python3 selftest_control.py > /tmp/scA.out 2>&1 & python3 selftest_control.py > /tmp/scB.out 2>&1; wait; grep -c "^PASS selftest_control" /tmp/scA.out /tmp/scB.out` prints 1 for each file (2 passes). Watched red on the base 2026-11-19 (0 passes of 2).

## refs
file: src/RimMandrake/rimflow/selftest_control.py

## criteria
- Two `selftest_control.py` runs started together on one machine both print `PASS selftest_control`.

## verify
cd src/RimMandrake/rimflow; python3 selftest_control.py > /tmp/scA.out 2>&1 & python3 selftest_control.py > /tmp/scB.out 2>&1; wait; grep -c "^PASS selftest_control" /tmp/scA.out /tmp/scB.out
