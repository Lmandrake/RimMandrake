# Polish: probe results

One line per finding judged not worth the touch. A record; nobody fixes from it.

- 2026-11-19 `RIMMANDRAKE_MOVE_OWN_UNREADABLE_CLASSES_ONTO_PROBE_TEN_LEFT`: ten pipeline files (boundary_check, findings_fold, heap_bisect, northstar_driver/bars, running_now, scratch_reap, conductor_closeout, mod_owner_hold, pipeline_control, pipeline_pause) keep their own Unreadable/Unmeasured exception. Each one already raises on "could not look", so none blurs the four answers. The move would change about 155 sites in pipeline code (the reaper and the owner-hold file among them) for uniformity only. The red oracle `own_unreadable_classes_gone_accept.py` checks a class name, not a behaviour.
