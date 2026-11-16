## spec
Pipeline defect, found 2026-11-16 on Contagion: `coverage_judge.grant_waits` made every granted release ("fix first,
then exactly one more look") wait on a re-pin (a `locked_change` after the stop), but `designer_stage.py repin` refuses
any concept whose `version/VERSION.json` is not `locked` (Contagion's reads `open: ...`). So Contagion's grant
(RIMMANDRAKE_FIX_CONTAGION_COVERAGE_GAPS_TWENTY_FIVE_ALL_SOUND, done) could never apply, and the owner's word for one
more look would have been refused. Fix: the re-pin is owed only by a locked concept; an unlocked one waits on its items.

## verify
`python3 src/RimMandrake/rimflow/selftest_coverage_judge_loop.py` prints PASS.

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_coverage_judge_loop.py` exits 0 with `PASS`; its new
`granted_unlocked` block (an open version file, and none at all) holds 4 checks, watched FAIL 4 on the base (each refusal
named "the re-pin"); the locked-concept checks in `granted` and `granted_late` still pass (fixtures now locked).
