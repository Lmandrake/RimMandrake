A <ITEM>.det.lock (or any 0-byte .lock) in the clone pool is a flock target: its existence never means a live run. Read the holder from /proc/locks (wrapup.clone_owner) or try a non-blocking flock before you call it live or stale. Until 2026-11-25 nothing removed these files, so 915 stood with no clone.
item: RIMMANDRAKE_CLEAN_STALE_LOCKS_AND_LEFTOVERS_OF_RETIRED_ERAS
home: infrastructure/state/facts/instrument_traps.md
