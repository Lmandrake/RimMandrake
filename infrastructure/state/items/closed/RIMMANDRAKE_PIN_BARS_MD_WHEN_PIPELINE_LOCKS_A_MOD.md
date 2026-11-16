# RIMMANDRAKE_PIN_BARS_MD_WHEN_PIPELINE_LOCKS_A_MOD

Found by the Stage 2 steward run of LeaningScrub 0.1.0 (RIMMANDRAKE_STEWARD_LEANINGSCRUB_PREFLIGHT_STAGE, 2026-11-16). LeaningScrub is the first mod whose Design Version the pipeline locked itself (`maturation_autonomy.autolock_and_land`, locked_by pipeline). That lock wrote VERSION.json, and `maturation.py lock-bars` wrote locked_bars.json, but nothing wrote `version/bars.md`: the git blob of each locked file at the lock commit. The re-pin rule (2026-11-14), the blind challenge's lane-1 inputs (`maturation.py`, `version/bars.md`) and every mod's preflight pin check read that file. Every hand lock (Graffiti, Pyrelands, FlowWorks, ExplosiveKnockback, GimmeSomeSlack) wrote one by hand.

## spec
`maturation.lock_bars`, on the first record of a version's bars, also writes `version/bars.md` (`maturation.pin_bars_md`): the blob of each of `LOCK_PINNED` (tree.json, sheet.md, scenes.json, floor.json, exam.json, record.json, plan.md, stage.json, coverage_verdict.json) at VERSION.json's `locked_from_commit`, for the files that exist there. It never rewrites an existing bars.md.

## criteria
- The first `lock-bars` of a locked version writes bars.md with one pin row per locked file present at the lock commit, and names the lock commit.
- A file absent at the lock commit gets no row; an existing bars.md is left alone.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation.py` prints ALL PASS. Watched failing 2026-11-16 on the base: `FAIL the first lock-bars pins each locked file that exists at locked_from_commit in version/bars.md (a pipeline lock had no pins)`, 1 failed; ALL PASS with the fix. Expected: 1 new check passing, every other check unchanged.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
