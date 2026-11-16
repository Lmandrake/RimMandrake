# RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR

## spec

Measured 2026-11-16 08:13 PST: the seat clone /home/mandrake/rm/bench held 150 dirty paths (21 modified, 129
untracked) and no alarm saw it: 92 conversation records (landed only at a handoff), 14 items whose ledger `file` event
was on origin but whose prose never landed, Designer edits, queue views, strays up to two weeks old. Cleaned by hand
the same morning (backup D:\ClaudeWork\rimmandrake\backups\bench_cleanup_2026-11-16\).
Fix: `src/RimMandrake/Utils/seat_dirt.py` lands the two always-safe classes (conversation records; untracked prose of
an item origin's ledger has filed and origin lacks) once they have settled 10 min, and counts every other path dirty
for over 60 min. ops_watch's disk family reads it as `disk.seat_dirt` (a live `run --file-alarms` pass tidies first);
rule `disk.seat_dirt > 0` raises the fixed alarm OPS_SEAT_CLONE_DIRT_RESTORE, routed to Operations.

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_seat_dirt selftest_ops_watch selftest_ops_watch_alarm_names`
(3 tests). selftest_seat_dirt fails on the base (no seat_dirt module); after: lands exactly the filed prose and the
conversation record, counts the unfiled prose and the old tracked edit (2), never the one-minute-old file.

## criteria

- A path dirty in the seat clone for over an hour that no safe class covers turns `disk.seat_dirt` above 0 and files
  OPS_SEAT_CLONE_DIRT_RESTORE; a fresh path never does.
- Conversation records and filed item prose land without a hand, from a temp index (the clone's index never touched).
