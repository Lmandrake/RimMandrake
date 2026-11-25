# Polish: the clone pool's admission and reuse

- `modcheck/suite.py` writes its fallback screenshot as a 24 MB BMP into the clone's `Transient/modcheck/` (31 in one
  clone, 0.7 GB, 2026-11-22). `shed` removes them at reuse. A PNG would be about 1/10 of the size.
- A standing `<ITEM>.det` clone that `take_clone` reuses for the same item is only synced, not shed (its own
  `Transient/` may be the rerun's input).
