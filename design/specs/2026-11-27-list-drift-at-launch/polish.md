# Polish beside design/specs/2026-11-27-list-drift-at-launch/boundary.md

- `src/RimMandrake/Utils/list_journal.py` `rows`: `TAIL_BYTES` (1 MiB) names no danger, and after roughly 4,000 rows
  with no modset_builder write of a list (about 250 bytes per launch row) `last_write` loses that write and the line
  reads "no modset_builder write of it on record". risk: not handled: a journal older than its tail reads a real write
  as none. Smallest fix: read the whole file (it grows one short row per write or launch), or name the danger beside
  the number.
