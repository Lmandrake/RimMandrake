# RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS

Owner, 2026-11-16 ~8:20 PM PST: *"Then run it in the pipeline on the 2nd game perhaps (ExplosiveKnockback) to see if it can get there itself?"*

## spec

MEASURED 8:15 PM PST 2026-11-16 (`maturation.py next`): ExplosiveKnockback has waited for its automatic blind cycle 5 since 1:43 PM and Pyrelands for blind cycle 3 since 2:28 PM; both read "NEXT (automatic: the Dispatch tick launches it)", exit tests passing, `steward_confirms: none in the request`. The game and bridge were free. Find why the Dispatch tick did not launch them, fix the pipeline so it does (tests first), and let the PIPELINE carry ExplosiveKnockback through blind cycle 5 and in-game visit 4 by itself, on the second game if the pipeline supports one, with no hand launch of a stage.

## refs

file: src/RimMandrake/rimflow/maturation_dispatch.py

## verify

A selftest that reproduces the wait (red on the base) and passes after the fix; then the live reading: the Dispatch tick's own launch record for ExplosiveKnockback blind cycle 5, with its time.

## criteria

- The cause is named with evidence, not guessed.
- The tick launches ExplosiveKnockback's next stage itself; no stage is run by hand.
- If the wait was a deliberate cap or schedule, that is reported with where it is set, and nothing is changed without saying so.
