# RIMMANDRAKE_CLEAR_PUBLISH_STUCK_ON_LEVEL_SHARD

## spec
`dispatcher.execute` keeps `publish_fail_since` from the first failed publish until one pushes. A tick whose publish
returns None (nothing unpublished on the DISPATCHER shard: `dispatcher.publish` returns None only when
`ingest.unpublished` is empty) did not clear it, though None proves the stopped commit reached origin another way
(the RUNNER ingest pushes in the same dispatch clone). Incident publish-20261117143919 rang on exactly this:
`publish KILLED after 6 s` at 13:59:59Z, twelve ticks 14:02-14:34Z each publishing in ~0.1 s with no journal row
(None; `tick_steps.jsonl`), `publish KILLED after 0 s` at 14:36:37Z, stuck = 36.6 min >= publish_stuck_s 1800, while
origin took pushes from the bench clone every few minutes (bench `git reflog origin/main` 05:59-07:34 PST).

Fix: None clears the stuck clock, as a push does. A kill that is followed only by more kills still alarms.

Files: src/RimMandrake/rimflow/dispatcher.py, src/RimMandrake/rimflow/selftest_dispatcher.py

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_dispatcher` — the two new checks in
`test_publish_young_lock_is_traffic` pass (the first watched failing before the fix: `{'publish:stuck': 2210.0}`).

## criteria
- a level shard (None) between two kills clears the stuck clock: no publish:stuck
- two kills >= publish_stuck_s apart with no level reading between still raise publish:stuck
