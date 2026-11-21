# Polish: one game lock (a record; nobody takes lines from it)

- `driver_lock` keeps every broken lock aside as `DRIVER_LOCK.json.broken.<stamp>.<pid>`; game a's scratch folder held
  about 270 of them on 2026-11-21, and nothing ever deletes one.
- `game_lock.py query b` and `query all` import `game_instance` (about 18 ms of the 48 ms) only to find game b's lock path.
