# Polish beside `boundary.md` (not part of passing)

- `lane_tickets_of` reads backticked bullets only; the 2026-11-19 census lane briefs list their tickets in a table, so
  a lane run of that form is continued on its own item only. Reading table rows too would hand off the way bullets do.
- The step's recheck reads the ledger of the clone it runs from, which may be behind origin/main; a fetch-free read of
  origin/main's shards would see a close published minutes before.
