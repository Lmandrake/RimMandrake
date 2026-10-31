# ARENA_CENSUS_FIXSHA_WRONG_COMMIT

Filed (BENCH): the arena census resolves wrong fix commits and misses unfiled rework.

## verify
- L0: on the frozen trial pool, a fixture of items with known fix commits resolves each to the right sha, and a planted
  unfiled rework commit is reported; selftest green; every pool row the corrected census changes is listed on this item.
- Stopping point: finish.

## criteria
- A1 L0: known fix shas resolve; planted rework found; changed rows listed
