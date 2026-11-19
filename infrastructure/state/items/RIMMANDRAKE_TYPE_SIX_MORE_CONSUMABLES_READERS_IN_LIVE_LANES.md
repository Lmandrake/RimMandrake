## spec
The rest of slice 2 of `design/specs/2026-11-18-pipeline-control-surface/03-merged.md` section 5, left by
RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO (c180799371, which typed pipeline_control's six counters:
granted_look, coverage_runs, coverage_not_covered, coverage_malformed, blind_cycles_visit, blind_cycles_total, as
control.py adjustments with compensating undo). Still counted only by their own readers, with no `pipe set|limit`:
automatic in-game runs, steward runs, launch retries, chained design runs, refusal counts, the stage spend ceiling; and
streaks (Test Pilot's three non-pass in a row) are not yet derived from ordered valid runs (critique 8). Each reader
lives in maturation_dispatch.py / maturation_autonomy.py / testq steward / role_launch, files other lanes were editing on
2026-11-18. Per consumable: add it to pipeline_control.RESOURCES with its measured count, route its reader through
PC.used / PC.limit, test the reader honours a set and a limit. Then retire pipeline_control's remaining journal (the
queue, with slice 3: RIMMANDRAKE_ADD_PIPE_QUEUE_VERBS_QUEUE_VIEW_PRINTS_MEGABYTES).
Acceptance test: none at filing, each consumable's reader decides its own test (written with the reader change, watched
red: `pipe set <Mod> <res> N` has no effect on that reader on base).

## refs
file: src/RimMandrake/rimflow/pipeline_control.py
file: src/RimMandrake/rimflow/control.py
file: design/specs/2026-11-18-pipeline-control-surface/03-merged.md

## criteria
- Each listed consumable is a RESOURCES row whose live reader goes through PC.used/PC.limit, each with a test.

## verify
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_pipeline_control,selftest_control
