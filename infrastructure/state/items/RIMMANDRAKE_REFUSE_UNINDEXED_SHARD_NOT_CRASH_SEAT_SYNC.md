# RIMMANDRAKE_REFUSE_UNINDEXED_SHARD_NOT_CRASH_SEAT_SYNC

## spec

Found in the full-file review of seat_sync.py (657a2a262a), 2026-11-16: dirty_merges called `_blob(g, staged)` for a
merge=union path with no index entry (staged None, e.g. a shard dropped with `git rm --cached` but still on disk), so
./sync and ./publish's move died with `TypeError: expected str, bytes or os.PathLike object, not NoneType` instead of
refusing with the path. Fix: no index entry is no snapshot; the path is stuck and the sync refuses naming it. Also the
module docstring now lists the ledger-lines and landed-twin rules plan() applies.

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_seat_sync_unindexed_shard selftest_seat_sync` (2 tests).
selftest_seat_sync_unindexed_shard watched FAIL on the base (the TypeError), PASS after (REFUSED naming the shard).

## criteria

- An unindexed shard that upstream also changed refuses the sync with the path, exit 1, no traceback.
