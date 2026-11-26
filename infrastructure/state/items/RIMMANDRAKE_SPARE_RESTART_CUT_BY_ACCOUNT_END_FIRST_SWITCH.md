# RIMMANDRAKE_SPARE_RESTART_CUT_BY_ACCOUNT_END_FIRST_SWITCH

## spec

`src/RimMandrake/rimflow/work_bundle.py` `plan_restart` has a progress guard: a restart run that ended no member of
its bundle raises an alarm, and the bundle is not restarted again. The guard counts only ended members. It does not
read why the restart run ended.

Failure that happened, 2026-11-26 3:35 AM PST, on the account plan's first real switch (steven to lukas): bundle
`WB-mod-FlowWorks-20261126-052154`, restart run `rm-detached-bench-rimmandrake-class-seven-thirst-fails-sit-1795688535`
on `RIMMANDRAKE_CLASS_SEVEN_THIRST_FAILS_SITE_FULL_OF_PATIENTS`. The run published repairs (`3dc910eb70`,
`fa0db5d03b`). The account-end stop order `ct_000209` then stopped it at an easy spot, with a `LEFT OPEN:` note. The
guard read "ended no member" and raised. `left_open_continue` then refused to carry the work on
(`DETACHED_CONTINUE_LIMIT_REACHED`). The bundle now waits for a hand.

Rule: a run that was stopped from outside the work spends no trial, turn or cycle (`CLAUDE.md` §Stops that the work
did not cause; `src/RimMandrake/rimflow/failure_class.py`).

Fix: a restart run whose end was not the work's own (an account-end stop, a stop by the owner or the Conductor, a
kill, a timeout, a run that never started) does not count for the progress guard. The bundle is restarted. A restart
run that ended by itself with no member ended still raises. A stop by hand that `HAND_KILL_RX` matches keeps its
present meaning (act `none`).

The guard exists against a bundle that restarts without end. Keep that protection: the fix must not let a bundle
restart without end when each restart ends by itself.

## refs

file: src/RimMandrake/rimflow/work_bundle.py
file: src/RimMandrake/rimflow/selftest_work_bundle.py
file: src/RimMandrake/rimflow/left_open_continue.py
file: src/RimMandrake/rimflow/failure_class.py

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_work_bundle`

Two new cases in `src/RimMandrake/rimflow/selftest_work_bundle.py`:
(a) a restart run that an account-end stop cut short, with no member ended, reads act `restart`. Red on the base
commit `494166fef6`, green on the fix.
(b) a restart run that ended by itself, with no member ended, reads act `raise`. Green on both.

Not seen red at filing: the fixer writes case (a) and shows it red first.

## criteria

- A restart that a stop from outside the work cut short is restarted, and does not count for the progress guard.
- A restart that ended by itself and ended no member still raises, with the same alarm text.
- On the live record of bundle `WB-mod-FlowWorks-20261126-052154`, the plan for the stopped run reads `restart`, or
  the bundle already has a later run on its open member.
