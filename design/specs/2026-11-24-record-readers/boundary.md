# BOUNDARY: readers of the shared run-record folder name what a run record is, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`RECORD_NAME`, `record_unit`, `is_record`, `record_units`,
`all_records`, `return_all`, `earlier_session_totals`), `src/RimMandrake/rimflow/stop_resume.py` (`recent_records`),
`src/RimMandrake/rimflow/maturation.py` (`live_twins`), `src/RimMandrake/Utils/fleet_mods.py` (`detached_done`).
Item: `RIMMANDRAKE_SCOPE_COULD_NOT_LOOK_ONE_STRAY_FILE_HELD_ELEVEN_TICKETS`. Why: on 2026-11-24 `all_records` read 123
`<unit>.alive.json` files (`run_alive.py`) as broken records, and `list_dispatch` held 11 ready items for about a day.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_record_readers.py`.

## ACCEPTS (the only inputs this is built for)

- **the-run-record-folder.** `<dispatcher state>/detached/`. Run records are `<unit>.json`, written whole by
  `write_record`, and a unit (`unit_name`) holds no dot. Other writers put files beside them: `<unit>.out.json`,
  `<unit>.alive.json`, `.err`, `.finish.log`, `.brief.md`, `.brief.src.md`, `.out.json.return` and `.jsonl` logs
  (census of the live folder, 2026-11-24: 1305 records, every one named `<unit>.json` with its own unit inside).

## DOES NOT SURVIVE (not promised)

- **a-foreign-dot-free-json-that-does-not-parse.** Another writer's file named `<word>.json` with no dot in `<word>`
  that is not JSON reads as an unreadable record. No writer makes one today (census above).
- **a-record-whose-unit-differs-from-its-name.** A record file whose `unit` is not its file name is not read as a
  record. `write_record` names the file from the unit, so none is made.

## PROMISES (each one is owed a test of the same name)

- **a-record-is-named-by-its-unit.** `record_unit(name)` is the unit of a file named `<unit>.json` whose stem holds no
  dot, else None. `is_record(rec, unit)` is true only for a dict whose `unit` is that unit.
- **all-records-reads-only-records.** `all_records` yields each record. A record file that cannot be read or parsed goes
  to `unreadable(name)`. A file that parses but does not name its unit, and every other writer's file, is not looked
  at. A folder that cannot be listed raises OSError: could not look is never "no records".
- **every-reader-of-the-folder-skips-other-writers-files.** `stop_resume.recent_records`, `maturation.live_twins`,
  `fleet_mods.detached_done`, `earlier_session_totals` and `return_all` take their records by `record_unit` and
  `is_record`: a sign-of-life file that copies a run's fields is never a run, a twin, a receipt, a session's tokens
  or a clone to return.

Later lists beside this page: `polish.md` (none yet).
