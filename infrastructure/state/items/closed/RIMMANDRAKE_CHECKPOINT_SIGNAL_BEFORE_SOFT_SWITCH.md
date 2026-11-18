## spec
Goal 2 of RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL (Conductor brief 2026-11-17 08:03), not built there: before a
planned switch (the plan's `soft`), detached runs get a checkpoint signal and a grace period, so they publish
before the fleet stop. Goals 1 and 3 (resume after a switch, park on a hard stop) landed at 938880262a.

## criteria
- a plan `soft` pass tells every live detached run to checkpoint (publish its green work) before the stop, and the stop waits a stated grace period
- no signal carries spend, cap or remainder

## verify
A selftest in src/RimMandrake/rimflow/ that drives a plan soft pass with stubbed detached runs and asserts the
signal and the grace period; then the next real soft switch, read from the conductor log.

## refs
file: src/RimMandrake/rimflow/stop_resume.py
file: src/RimMandrake/Utils/switching_plan.py
item: RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL
