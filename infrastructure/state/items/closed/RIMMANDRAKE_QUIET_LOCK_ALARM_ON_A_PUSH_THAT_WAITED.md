## Problem

The Dispatcher's publish step raised `publish:index_lock` (incident publish-20261116020910, 2026-11-16 02:06Z) on the
result `waited 0.3 s for another git's index.lock; pushed`: a publish that waited out another git and then pushed.
`jam` in `dispatcher.py` matched any result containing `index.lock` except the young-lock traffic wording.

## Fix

`jam` now also requires that the publish did not push (`pushed` or `…; pushed` is a success).

## Acceptance test

`python3 src/RimMandrake/rimflow/selftest_dispatcher.py` → `0 failure(s)`. The new case in
`test_publish_young_lock_is_traffic` failed on the base (1 failure, the alarm rang), and passes with the fix;
`selftest_dispatcher_mut.py` stays at 0 failures.
