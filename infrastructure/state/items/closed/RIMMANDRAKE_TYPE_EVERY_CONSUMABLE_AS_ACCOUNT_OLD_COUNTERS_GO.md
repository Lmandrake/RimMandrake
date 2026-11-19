# RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO

## spec
Slice 2 of `design/specs/2026-11-18-pipeline-control-surface/03-merged.md` section 5: every other consumable
(blind cycles per visit, automatic in-game runs, steward runs, launch retries, chained design runs, refusal counts, the
stage spend ceiling, the coverage caps) becomes a typed account in `src/RimMandrake/rimflow/control.py` with opening
balances imported from today's records; `pipe set <Mod> <res> <N>` and `pipe undo <act>` as compensating acts
(critique 16: set -> set -> undo first keeps the later set; grant -> consume -> undo grant shows the deficit); streaks
derived from ordered valid runs (critique 8); then the old counter readers (`pipeline_control.py` journal counts,
run_void book moves) are deleted, reconciled against the store first. Slice 1 is item
RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS.

## verify
Acceptance test: `RM_CONTROL_DB=/tmp/acc2.db python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import control as C; C.init(); C.set_account('Graffiti','blind_cycles_visit',0,'t'); C.undo(C.log(1)[0].split()[0],'t')"  (exit 1 on 5dfb7ed767+: no set_account/undo; watched 2026-11-18 1:25 PM PST). The builder writes the full selftest first: critique 8's three cases and critique 16's four.`

## criteria
The acceptance command above passes, and the builder's new selftest (written first, watched failing) passes.

## refs
file: src/RimMandrake/rimflow/control.py
file: design/specs/2026-11-18-pipeline-control-surface/03-merged.md
