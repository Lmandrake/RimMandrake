## spec

You are the second reader. Read `design/specs/2026-11-23-sort-old-list-tickets/second_reader_brief.md` first and do exactly what it says. Your batches:
- `RIMMANDRAKE_SORT_OLD_SHIPS_DROIDS_AND_GUNS_PART_TWO_OF_TWO`
- `RIMMANDRAKE_SORT_OLD_CREATURES_PART_ONE_OF_TWO`
- `RIMMANDRAKE_SORT_OLD_CREATURES_PART_TWO_OF_TWO`
- `RIMMANDRAKE_SORT_OLD_PLANTS_AND_FOOD_TICKETS_IN_ONE_PART`
- `RIMMANDRAKE_SORT_OLD_WATER_AND_WEATHER_PART_ONE_OF_THREE`
- `RIMMANDRAKE_SORT_OLD_WATER_AND_WEATHER_PART_TWO_OF_THREE`
- `RIMMANDRAKE_SORT_OLD_WATER_AND_WEATHER_PART_THREE_OF_THREE`

## verify

`python3 design/specs/2026-11-23-sort-old-list-tickets/second_read_check.py RIMMANDRAKE_READ_REMOVED_OLD_TICKETS_AGAIN_NEXT_SEVEN_BATCHES` prints HOLDS.

## criteria

- each sampled removal is read and has a verdict, a batch over one wrong in ten is read whole, and each wrong removal is restored.
