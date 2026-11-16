## spec
Plan `design/plans/2026-11-14-maturation-pipeline-build.md` slice 2, second half, and
`design/RimMandrake/maturation_pipeline.md` §9 "Designed but not built": `maturation.py advance` refusals go through
`refusal_contract.submit`, so a stage refused again and again raises `REFUSAL_NOTHING_COULD_EVER_PASS` instead of
looping. Today `maturation.py` calls `RC.check` on a verdict (line ~653) but never `RC.submit`, so repeated advance
refusals count nowhere. Found by the pipeline sleeper census (`design/RimMandrake/pipeline_sleepers_census_2026-11-15.md`).

Acceptance test: none written yet, because the plan's own test (`RM_REFUSAL_DIR=<tmp> python3
src/RimMandrake/rimflow/selftest_maturation.py --submit`) PASSES on base 464c69ccf0 (the flag is ignored), so it is not
an oracle. The builder writes first a case that runs a refused `advance` in a sandbox with `RM_REFUSAL_DIR` set and
asserts one submitted row there (and the alarm row after the repeat limit), watches it fail on base, then builds.
