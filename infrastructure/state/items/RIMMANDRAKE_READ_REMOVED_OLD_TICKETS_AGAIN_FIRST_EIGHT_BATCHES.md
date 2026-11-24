## spec

You are the second reader. Read `design/specs/2026-11-23-sort-old-list-tickets/second_reader_brief.md` first and do exactly what it says. Your batches:
- `RIMMANDRAKE_SORT_OLD_STEVEDESKTOP_TICKETS_IN_ONE_PART`
- `RIMMANDRAKE_SORT_OLD_OPS_ALARMS_TICKETS_IN_ONE_PART`
- `RIMMANDRAKE_SORT_OLD_HARNESS_AND_PROOFS_PART_ONE_OF_THREE`
- `RIMMANDRAKE_SORT_OLD_HARNESS_AND_PROOFS_PART_TWO_OF_THREE`
- `RIMMANDRAKE_SORT_OLD_HARNESS_AND_PROOFS_PART_THREE_OF_THREE`
- `RIMMANDRAKE_SORT_OLD_BRIDGE_AND_GAMES_TICKETS_IN_ONE_PART`
- `RIMMANDRAKE_SORT_OLD_PIPELINE_TOOLS_PART_ONE_OF_FOUR`
- `RIMMANDRAKE_SORT_OLD_PIPELINE_TOOLS_PART_TWO_OF_FOUR`

## verify

`python3 design/specs/2026-11-23-sort-old-list-tickets/second_read_check.py RIMMANDRAKE_READ_REMOVED_OLD_TICKETS_AGAIN_FIRST_EIGHT_BATCHES` prints HOLDS.

## criteria

- each sampled removal is read and has a verdict, a batch over one wrong in ten is read whole, and each wrong removal is restored.
