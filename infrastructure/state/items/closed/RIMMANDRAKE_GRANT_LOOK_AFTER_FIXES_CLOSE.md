# RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE

## spec

His card on Pyrelands 2026-11-15 ("Fix the 17 gaps, one final look"; record.json decision
d_fix_seventeen_round_six_gaps, OWNER:1794774724955142310) could not be written down as data: a coverage release
(`coverage_judge.py release`) takes effect at once, so "fix first, then exactly one more look" lived only in prose,
and after that look a not_covered paused the mod as a Conductor line, not as his card with its evidence.

Fix: `coverage_judge.py release <dir> --why ... --after ITEM [--after ITEM]` records a granted release
(stage.json `coverage_release_granted`, history `coverage_release_granted`) and leaves the stop standing. It takes
effect only through a later `release` (the locked-change chain steward's) once every named item is closed and a
locked_change (the re-pin) is newer than the grant; before that a release is refused, naming what it waits on. Applied,
it is one release (one look), marked final. A stop after a final look is the owner's: the tick shows an OWNER row with
a card quoting the stop and pointing at coverage_verdict.json, and no chain steward releases again on its own.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_coverage_judge_loop.py` (granted release: recorded, refused
while the item is open or the re-pin missing, applied once both hold, one look, final) and
`selftest_maturation_autonomy.py` ("final look": a stop after a final look is an OWNER card naming
coverage_verdict.json, even after a later locked change). Both fail on 437b7391b3.
