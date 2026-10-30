arena_tasks freeze now refuses a Clean label until its 7-day label_window_ends has passed; the real pool (2 Clean, latest window ends 2026-11-02T00:21Z, Escaped up to 11-03) cannot be frozen before ~2026-11-03. Plan the trial start after that, or freeze Escaped-only.
home: src/RimMandrake/Utils/arena/arena_tasks.py
