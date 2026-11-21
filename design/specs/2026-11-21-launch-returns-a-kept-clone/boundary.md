# BOUNDARY: the launch gives back a pool clone that a finished run's return kept, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`hold_until_returned`, `kept_by_return`, `kept_why`, `return_clone`,
the notes in `_launch`). Item `RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_FOUR`, written 2026-11-21. The
ruling: `design/RimMandrake/standing_rulings.md` §A fault of form is repaired where it is found. Each promise has a
test of its name in `src/RimMandrake/rimflow/selftest_detached_helper.py`.

Why: on 2026-11-21 at about 1:40 PM PST the tick's launch of `RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_THREE_FAILURES_BACK`
was refused twice. The refusal said that the clone `<ITEM>.det` was held by four finished runs. Each run's return had
kept the clone because a process of another run was working in it. When the refusal came, no process was in the clone.
The refusal named its own repair (`detached_helper.py return --unit <unit>`). Each held run's record said "its return
step left no steps", because a return that kept the clone wrote nothing.

## ACCEPTS (the only inputs this is built for)

- **a-pool-clone-dest.** The path `<pool>/clones/<ITEM>.det` (or a resume's `<ITEM>.r<epoch>.det`) that `launch` is
  about to take, and the run records under the dispatcher state's `detached/`.

## DOES NOT SURVIVE (not promised)

- **two-launches-at-once.** Two launches of one item that both find the same kept holder can both run its return. The
  second return reads `already returned` and changes nothing.
- **a-return-that-hangs.** The launcher waits for its own return as long as the return runs. A return bounds its own
  steps (publish 300 s, sync 300 s).

## PROMISES (each one is owed a test of the same name)

- **a-kept-clone-is-returned-by-the-launch.** When every run that holds the clone is a finished run whose return kept
  it (its unit and its `-return` unit are gone, and its record does not read `returned`), the launch runs that return
  itself, once per run, then checks again and goes on. The launch text ends with one line that starts
  `NOTE (form, repaired): ` for each run that it returned, and that line names the unit. Red on the base: refused.
- **a-return-that-keeps-again-is-refused-with-its-reason.** When the launcher's own return keeps the clone again, the
  launch is refused before any sync or unit. The text names `return --unit <unit>`, `--clone <dest>` and the reason
  the return gave. The launch runs each return only once.
- **a-live-or-dead-holder-is-never-returned-by-the-launch.** A run that is running, launching, dead (its unit is gone
  and its finish never ran) or still giving the clone back is never returned by the launch. A kept run beside a live
  one is not returned either. Those cases are refused or waited for, as before.
- **a-kept-return-records-why.** A `return_clone` that keeps a finished run's clone because a process works in it, or
  because another live run holds it, writes that reason into the record's `return_steps`. It never sets `returned`. A
  later refusal names the reason, never "its return step left no steps". Red on the base: no steps.

## LIMITS

- **One return per held run per launch.** Danger: a launch that loops on a return that keeps the clone every time.
  Evidence: the base refused, and the tick launched again on every tick (two refusals in one hour, 2026-11-21).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
