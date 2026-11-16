# RIMMANDRAKE_FIX_DISPATCH_VIEWS_LANDED_BLIND_TO_PEER_SHARDS

Caused by RIMMANDRAKE_ADVANCE_FLOWWORKS_PAST_OFFLINE_BUILD (steward run, 2026-11-16).

## spec
The Dispatch's `land_ledger` (`src/RimMandrake/rimflow/maturation_dispatch.py`) lands a mod's DISPATCH shard AND its derived views with `land.sh -m`, which writes the worktree's whole files onto origin/main's tree. The views are built from the Dispatch clone's local shards; when a holder run's shard landed on origin from another clone and the Dispatch clone has not pulled it, the landed views drop that shard and overwrite the peer's correct views. Seen 2026-11-16: fa045999a4 (04:05, holder note, views include HOLDER.run-1794830532) then 10fd00c9cf (04:07, "modledger: run.end of ended pilot runs (Dispatch step)", views built without that shard). origin/main then failed `selftest_modledger_tree.py` (VIEW_STALE, 3 views of ExplosiveKnockback) and every ./publish touching a pipeline file was refused until 41e277c3e7 rebuilt them by hand-free `modledger.py views --mod ExplosiveKnockback`.
Fix: the views land_ledger lands are built from origin/main's shards (fetched at landing) plus the Dispatch's own DISPATCH shard, without overwriting other writers' files in the root; a peer shard the root lacks is never dropped from a landed view.

## verify
New selftest case in `src/RimMandrake/rimflow/selftest_maturation_dispatch.py` (or a sibling): a fixture origin holds a mod ledger with a peer HOLDER shard and its views; a Dispatch root cloned before that shard landed appends to DISPATCH.jsonl and runs land_ledger; the views on origin afterwards list the peer shard and `modledger.py lint`/tree check reports 0 VIEW_STALE.

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py` with the new case: FAILS at 41e277c3e7 (landed views lack the peer shard), PASSES on the fix; every existing case still passes. The fixer records watching it fail before the fix.
