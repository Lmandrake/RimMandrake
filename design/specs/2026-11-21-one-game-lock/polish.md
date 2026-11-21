# Polish: one game lock (a record; nobody takes lines from it)

- `driver_lock` keeps every broken lock aside as `DRIVER_LOCK.json.broken.<stamp>.<pid>`; game a's scratch folder held
  about 270 of them on 2026-11-21, and nothing ever deletes one.
- `game_lock.py query b` and `query all` import `game_instance` (about 18 ms of the 48 ms) only to find game b's lock path.
- `rimflow bridge take` and `release` refuse his OWNER hold with exit 2 (`die`'s default), not 3 as `game_lock.py`
  does; no caller reads the code apart from 0 (fresh read, 2026-11-21).
- `host_guard.py take` refuses his OWNER hold with exit 75, not 3 (fresh read, 2026-11-21).
- `game_lock.run` never refreshes the lock's heartbeat; it matters only for a reader that cannot inspect the holder
  (another machine) (fresh read, 2026-11-21).
- `driver_lock._fence_identity` records no distro, so a Windows caller judges a WSL fence by its age only (60 s)
  (fresh read, 2026-11-21).
