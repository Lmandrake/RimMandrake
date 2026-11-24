# Polish: one live ledger run per mod

A record. Nobody takes lines from it for now.

- `live_unread` is said only on a `live` row; a held or paused row omits it.
- `stop_live` reads raw `gather`, so it misses a run that only `own_live` sees (a record that names no mod).
- The builder launch test takes the `red` kind only, not `red_seen` (one code path, one env).
- `end_ledger_runs` never books the end of a ledger run whose unit died unfinished and that no placement read; the mod
  is free (the unit is measured gone), only the book entry stays open.
- Codex review 2026-11-24, not significant in ordinary operation (unreadable_record_status_announces_wait_over, `maturation_dispatch.py:3590`): A booked holder exits normally, but a temporary read error makes its detached record unavailable across a tick. Dispatch correctly keeps the mod blocked. The displayed tick row hides the unreadable-record reason, and `status` can then print `the wait is over` as soon as systemd reports the unit inactive, even though the next ...
- Codex review 2026-11-24, not significant in ordinary operation (cooperative_stop_unreadable_record, `selftest_one_live_run_per_mod.py:247`): A pilot steward advances its mod to pre_human and receives an at-easy-spot stop. If that unit's record cannot be read on the next tick while the unit is still working, the tests would let a second steward and lease through. The pending-stop fixture keeps the record readable, and the unreadable-record fixtures leave the unit ...
- Codex review 2026-11-24, not significant in ordinary operation (same_visit_older_mod_failure, `selftest_live_kinds.py:227`): In one kind B visit, a driver records MOD FAILURE on build A, fixes it and records SUCCESS with valid mod_fix evidence on B, then rebuilds for another check and records one ENVIRONMENT FAULT on C. The changed test would pass an exit reader that reports this sequence as MOD failure even though C has only a spoiled run.
