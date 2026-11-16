# RIMMANDRAKE_REBUILD_DISPATCH_VIEWS_ON_EACH_LAND_RETRY

Caused by RIMMANDRAKE_ADVANCE_FLOWWORKS_PAST_OFFLINE_BUILD (steward run, 2026-11-16).

## spec
7b1ff1b4d545 (`origin_views()` in `src/RimMandrake/rimflow/maturation_dispatch.py`) rebuilds a mod's views from origin/main's shards plus the Dispatch's DISPATCH shard before `land_ledger` lands them. If a peer lands a new shard for that mod after that fetch and before land.sh's push, land.sh's non-fast-forward retry re-lands the SAME views, so origin/main reads VIEW_STALE until the next Dispatch landing (publish refuses pipeline changes meanwhile). Fix: rebuild the views on every land retry (or land the DISPATCH shard alone and let the views rebuild after a refused push).

## verify
A selftest case beside `land_views_main` in `src/RimMandrake/rimflow/selftest_maturation_dispatch.py` injects a peer shard landing between origin_views' fetch and the push (a land.sh hook or fx seam) and asserts origin's views list it with no VIEW_STALE.

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py` with that new case: fails at 7b1ff1b4d545, passes on the fix, every existing case still passes (177 at filing). Not watched failing at filing: the case needs a race seam that does not exist yet; the fixer records it red first.
