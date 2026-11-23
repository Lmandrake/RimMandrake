## spec
Filed 2026-11-23 about 2:45 AM PST by the run on `RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST` (live proof 2
of the List Pipeline's Work stage: recovery after a run is killed). A real debt of the same kind as
`RIMMANDRAKE_WRITE_MODS_WEEK_INTO_GOALS_PRODUCERS_ONLY_INPUT`: his directions of Sun 2026-11-22 10:47 PM and 10:48 PM
PST (ledger, OWNER note on `RIMMANDRAKE_RESUME_PLAN_RUN_WITH_HIS_SECOND_PIPELINE_DIRECTION`; full text in
`design/RimMandrake/standing_rulings.md` §The list's worker is a pipeline in its own right) are not a goal in
`infrastructure/state/CONDUCTOR_GOALS.md`, the Producer's only input.

Do: in `infrastructure/state/CONDUCTOR_GOALS.md`, in the newest block (or a new block on top if none covers
2026-11-22), add one goal whose text contains the exact sentence: The List Pipeline runs without the Conductor.
Follow it with one line: the list's worker is a pipeline with stages, shown on the Maturation Pipeline page, and a
pipeline that always needs the Conductor is incomplete (his words, cited from the ledger).

The crash proof: after `./publish` prints PUBLISHED, write the note `PUBLISHED <sha>; holding for the crash proof` on
this item, then run `python3 -c "import time; time.sleep(900)"` in the foreground, and only then close the item. The
proof stops the run during that wait on purpose: the List Pipeline's next tick must find the check holding and close
the item itself.

What would pass the check and leave the need unmet: the sentence written outside a goal block. The run writes it as a
goal.

## criteria
- `infrastructure/state/CONDUCTOR_GOALS.md` holds the goal "The List Pipeline runs without the Conductor".
- The item is closed by the lane's tick (role unit `rm-list-dispatch.service`), not by the run, after the run is killed.

## verify
python3 src/RimMandrake/rimflow/list_effect.py check 'path-has:infrastructure/state/CONDUCTOR_GOALS.md::The List Pipeline runs without the Conductor'   # holds
