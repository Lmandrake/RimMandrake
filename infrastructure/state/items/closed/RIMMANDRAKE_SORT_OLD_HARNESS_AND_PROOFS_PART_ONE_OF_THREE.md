## spec

You are the reader of this batch. Read `design/specs/2026-11-23-sort-old-list-tickets/reader_brief.md` first and do exactly what it says: it is
the whole job. The batch is the key `RIMMANDRAKE_SORT_OLD_HARNESS_AND_PROOFS_PART_ONE_OF_THREE` in `design/specs/2026-11-23-sort-old-list-tickets/batches.json` (34 tickets).
Read nothing else of the rule files beyond what the reader brief names.

## verify

`python3 design/specs/2026-11-23-sort-old-list-tickets/sort_batch_accept.py check RIMMANDRAKE_SORT_OLD_HARNESS_AND_PROOFS_PART_ONE_OF_THREE` prints HOLDS.

## criteria

- each ticket of the batch has one class and one evidence line, and the ledger agrees with the class.
