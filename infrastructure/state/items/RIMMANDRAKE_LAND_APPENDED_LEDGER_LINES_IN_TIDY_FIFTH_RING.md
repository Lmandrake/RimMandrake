# RIMMANDRAKE_LAND_APPENDED_LEDGER_LINES_IN_TIDY_FIFTH_RING

## spec

`disk.seat_dirt` (alarm OPS_SEAT_CLONE_DIRT_RESTORE_VTLF) rang five times for one cause: 2026-11-19, 11-20, 11-22
(twice) and 11-23 08:00Z. A window appends a rimflow ledger event line in the bench seat clone and does not land it.
`seat_dirt.classify` has no safe class for a ledger shard, so the line goes stale after 60 min, the alarm rings, an
Operations run is spent, and a hand land clears it (11-23: PUBLISHED 7ee54a6448).

Add a safe class to `src/RimMandrake/Utils/seat_dirt.py`: a path under `infrastructure/state/ledger/events/*.jsonl`
whose diff against HEAD is only appended lines. The tidy lands those lines on top of origin's copy of the shard. It
never writes the whole file: a clone behind origin would lose origin's newer lines (707fe0c64d). A shard that lost or
changed a line is never a safe class. The land runs in rm-seat-tidy.timer (`tidy --all --apply`), never in the
ops_watch sense phase.

The Operations fold of 2026-11-22 14:16Z set this down for the Conductor's word, because the timer writes in the
Conductor's own clone. The same timer already lands conversation records and item prose there.

## verify

`python3 src/RimMandrake/Utils/selftest_seat_dirt_ledger_append.py` prints 3 ok, 0 FAIL. Seen red on base
2026-11-23 (2 FAIL: cases a and c). Add a tidy-level case to it: origin's newer line and the clone's appended line are
both in origin's shard after the land.

## criteria

- An appended ledger line in a seat or role clone lands within two tidy passes; `disk.seat_dirt` does not ring for it.
- A shard with a removed or changed line stays counted as dirt.
- No ledger line on origin is lost by a land.

## refs

file: src/RimMandrake/Utils/seat_dirt.py
file: src/RimMandrake/Utils/selftest_seat_dirt_ledger_append.py
