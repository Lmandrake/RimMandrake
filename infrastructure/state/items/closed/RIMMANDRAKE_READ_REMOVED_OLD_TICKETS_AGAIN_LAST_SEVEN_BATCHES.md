## spec

You are the second reader. Read `design/specs/2026-11-23-sort-old-list-tickets/second_reader_brief.md` first and do exactly what it says. Your batches:
- `RIMMANDRAKE_SORT_OLD_BIOMES_AND_MAPS_PART_ONE_OF_FIVE`
- `RIMMANDRAKE_SORT_OLD_BIOMES_AND_MAPS_PART_TWO_OF_FIVE`
- `RIMMANDRAKE_SORT_OLD_BIOMES_AND_MAPS_PART_THREE_OF_FIVE`
- `RIMMANDRAKE_SORT_OLD_BIOMES_AND_MAPS_PART_FOUR_OF_FIVE`
- `RIMMANDRAKE_SORT_OLD_BIOMES_AND_MAPS_PART_FIVE_OF_FIVE`
- `RIMMANDRAKE_SORT_OLD_MIXED_SUBJECTS_PART_ONE_OF_TWO`
- `RIMMANDRAKE_SORT_OLD_MIXED_SUBJECTS_PART_TWO_OF_TWO`

## verify

`python3 design/specs/2026-11-23-sort-old-list-tickets/second_read_check.py RIMMANDRAKE_READ_REMOVED_OLD_TICKETS_AGAIN_LAST_SEVEN_BATCHES` prints HOLDS.

## criteria

- each sampled removal is read and has a verdict, a batch over one wrong in ten is read whole, and each wrong removal is restored.
