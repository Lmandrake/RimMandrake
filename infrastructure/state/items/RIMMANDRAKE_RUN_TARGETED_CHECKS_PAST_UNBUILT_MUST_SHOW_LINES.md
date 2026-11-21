# RIMMANDRAKE_RUN_TARGETED_CHECKS_PAST_UNBUILT_MUST_SHOW_LINES

## spec
A failure happened. `testq-sweep.service` failed at 2026-11-20 01:31 PST (09:31Z) and stays failed:
`REFUSED: validated must-show lines no component claims: drained_hole_is_a_prison, geyser_pit_is_a_hot_tub,
liquid_coating_washes_off, toss_flame_from_rim`. The Dispatcher raised it as `timer:testq-sweep.service` with no safe
automatic repair.

Cause, read from the code: on 2026-11-19 7:31 PM PST commit `82e59b2d76` added four must-show lines to FlowWorks's
north star for bars he kept in 0.1.0 and re-validated it. Those bars are still being built, so no modcheck component
claims them. `modcheck/runner.refusal` then refuses EVERY modcheck run of FlowWorks, targeted ones too
(`runner.run`, `runner.run_suite`, and `cli.py run --preview` for testq). Measured on 03fb15bf28:
`modcheck run FlowWorks --chains pit_exposure --preview` prints that REFUSED line. So no stage-6 check of FlowWorks
can run through modcheck or testq until the last new bar is built, and the same happens to any mod whose walk gains a
line for a bar not built yet (GimmeSomeSlack 0.1.1 next).

Fix: the uncovered lines stay fatal where they decide, the FULL run (refused, recorded, never green). A TARGETED run
(chains, rows or an item) is not refused by them: it tests what is built, never writes the full-suite status entry and
never greens the mod. An orphaned `shows=` (a typo) still refuses every run. The full preview prints
`FLOOR_UNCOVERED [...]`, and `testq sweep` then queues the mod's chains, not a `--full` job that the worker would
refuse after a deploy and a load.

## criteria
- `runner.refusal(fl, targeted=True)` is "" for an uncovered line and names an orphan; the untargeted form refuses.
- `run_suite(..., targeted=True)` runs past the floor; without it the suite is refused.
- `testq sweep` of a mod whose full preview names uncovered lines queues chains, never `--full`.
- The real input: `modcheck run FlowWorks --chains pit_exposure --preview` is not refused.
- `testq-sweep.service` runs green on its next timer firing (live promise).

## verify
Acceptance test: `python3 src/RimMandrake/Utils/modcheck/selftest_floor_targeted.py` exits 0 with
`selftest_floor_targeted: PASS (0 failed)` (5 checks pass). Watched red on 03fb15bf28: `FAIL (4 failed)` (two
TypeErrors on the new `targeted` argument, a `--full` sweep job queued, the live FlowWorks preview REFUSED).
Live: `systemctl --user start testq-sweep.service` exits 0.
