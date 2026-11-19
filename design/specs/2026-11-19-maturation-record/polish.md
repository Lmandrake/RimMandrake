# POLISH: maturation.py's stage record (beside `boundary.md`)

Review claims that break no promise on the page and that no ordinary input reaches; one line each.

- `next_version` reads the record outside `_mod_lock` and calls `commit_move` without `expect`: a stage move landing
  between the two is overwritten. Rare: next-version is a Conductor's hand act on a passed or newly locked version
  (Codex review 2026-11-18, seen while fixing its point 3).
- `seed_mod` writes the record without `_mod_lock`, only when no record exists yet (two first seeds at once).
