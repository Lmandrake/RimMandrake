seat_restart cooldown_until guards only the backstop, never a request, and handoff.py returns rc 0 on ALREADY HANDED OFF, so any fire-on-handoff loop would spin a fresh window for ever. _handoff_spin refuses a handoff inside the cooldown from a window with no work since its restart, and alarms.
home: src/RimMandrake/rimflow/seat_restart.py
