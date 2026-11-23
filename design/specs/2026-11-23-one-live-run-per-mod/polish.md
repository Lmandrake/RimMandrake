# Polish: one live ledger run per mod

A record. Nobody takes lines from it for now.

- `live_unread` is said only on a `live` row; a held or paused row omits it.
- `stop_live` reads raw `gather`, so it misses a run that only `own_live` sees (a record that names no mod).
- The builder launch test takes the `red` kind only, not `red_seen` (one code path, one env).
- `end_ledger_runs` never books the end of a ledger run whose unit died unfinished and that no placement read; the mod
  is free (the unit is measured gone), only the book entry stays open.
