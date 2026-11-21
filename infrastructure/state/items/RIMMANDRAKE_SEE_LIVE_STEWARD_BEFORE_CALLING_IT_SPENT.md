# RIMMANDRAKE_SEE_LIVE_STEWARD_BEFORE_CALLING_IT_SPENT

## spec
A failure happened. At 2026-11-20 4:47 PM PST the Dispatch tick read GimmeSomeSlack (Preflight, Stage 2) as
`steward_spent (paused)`: "the automatic steward run on this state
(rm-detached-bench-rimmandrake-steward-gimmesomeslack-prefl-1795220569) ended and the state has not moved; un-pause:
`maturation_dispatch.py clear GimmeSomeSlack --why ...`". That unit was still running (`systemctl --user is-active`
read `active`, and `maturation_now.gather` listed it `live: True`). 24 minutes into the run, the status page called it
ended. A Conductor who obeyed the un-pause line would have launched a second steward on the same state beside the live one.

Cause: `maturation_autonomy._gate` reads a key in `s["steward"]` (or `s["fixers"]`) as spent without a check of the
mod's live units. The in-game stage escaped the fault because `decide` puts a live unit to `live` first. Preflight, Designer
and every other stage that `decide` sends through `not_offline` to `_route` did not escape it.

Fix: `_gate` takes the mod's `live_units`. When the key's own unit is among them, `_gate` returns `("live", "<unit> is
live on it ...")`, and the row waits on that unit. A run that has ended still reads spent, as before.

## criteria
- A steward whose own unit is live a tick after its launch reads `wait`/`live`, never `steward_spent`. No second launch.
- When the unit has ended and the state has not moved, the key reads `steward_spent`, as before.

## verify
`python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` with the `live_steward_checks` rows. 4 rows: 2
stages (in_game, preflight) x (live waits, ended is spent). Seen red before the fix: `FAIL live steward (preflight):
... read paused/steward_spent`, 1 FAIL. Green after the fix: ALL PASS. Also green: selftest_maturation_hands,
selftest_pipeline_control, selftest_maturation_dispatch, selftest_maturation.

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/selftest_maturation_autonomy.py
