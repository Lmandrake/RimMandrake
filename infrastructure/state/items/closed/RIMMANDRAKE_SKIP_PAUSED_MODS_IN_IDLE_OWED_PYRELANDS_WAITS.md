# RIMMANDRAKE_SKIP_PAUSED_MODS_IN_IDLE_OWED_PYRELANDS_WAITS

## Problem
`maturation_dispatch.reading()` (src/RimMandrake/rimflow/maturation_dispatch.py, ~line 938) counts a mod whose row is
`klass == "paused"` as idle owed. Pyrelands sits at offline_build, owed "ready to advance", PAUSED on purpose
(coverage judging stopped 2026-11-15T14:05Z, REFUSAL_NOTHING_COULD_EVER_PASS, waiting on his card), so
`maturation.idle_owed_max_min` read 245-250 min (MEASURED 11:37 PST) and keeps OPS_MATURATION_IDLE_ADVANCING_MOD_CBFQ
and incident unrouted-20261102214722 open on a deliberate pause. A paused mod is already reported in `rd["paused"]`.

## Fix
Exclude rows with `klass == "paused"` from `owed` in `reading()`; a row with no klass still counts. Add the cases
to selftest_maturation_dispatch.py.

## Acceptance test
`python3 infrastructure/state/items/accept/RIMMANDRAKE_SKIP_PAUSED_MODS_IN_IDLE_OWED_PYRELANDS_WAITS.py` from the repo root: 5 cases, exit 0 with 5 PASS.
Watched it fail on base 4524281595: 2 FAIL (paused rows counted), 3 PASS, rc 1.
