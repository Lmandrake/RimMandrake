# ROUND_SERIES_FIX_SAME_SECOND_RESTART

src/RimMandrake/Utils/art_eval/round_series.py `resets()` attaches a stop when `stop.at >= reset.at`; both stamps are
whole seconds. A `fauna_drive.py stop` then `reset` (owner re-asks) within the same second leaves the new series
reading STOPPED, so the restart silently does nothing. Fails safe (nothing regenerated), hence not severe.

Failing-test sketch: add_stop(D, now=T); add_reset(D, now=T); stopped(D) must be None.
Fix direction: break ties by file order (a later line wins), or record a sequence number per line.
Found by full-file review (FOUNDRY 2026-10-24).
