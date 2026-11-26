# Work bundle WB-item-RIMMANDRAKE-DECIDE-RETIRED-ROLE-DUTIES-NOBODY-DOES-NOW-20261126-024244

System: item:RIMMANDRAKE_DECIDE_RETIRED_ROLE_DUTIES_NOBODY_DOES_NOW. One member, one group.

## Group 1 (done): RIMMANDRAKE_DECIDE_RETIRED_ROLE_DUTIES_NOBODY_DOES_NOW, class REAL

- Work: the P-5 age line in `src/RimMandrake/rimflow/list_dispatch.py` (`Openings`, `block_age`, gather and decide),
  settings `block_idle_days` and `block_window_min` in `list_dispatch.json`, `list_effect._world(observe=)`, promise
  `blocked-idle-window-open-is-due` on `design/specs/2026-11-23-list-dispatch/boundary.md`.
- Commits: 113ca7d01e08 (the age line), dac6157323a2 (fresh-reader fix: an item already due by age names its block too),
  1b8a0f1044fd (polish).
- Test: `t_blocked_idle_window_open_is_due` red on the parent (no `Openings`), red on two planted faults, green on the
  build. Item check `list_shape.py holds`: HOLDS.
- Live reading: rm-list-dispatch.timer, from 7:37 PM PST 2026-11-25: Shape runs on WASTELAND_MECHANICS_BUILD_1 and
  SCRAPPER_PIPE_REDRAW_ASKED_TWICE_NOW lifted both stale blocks and gave each its mod's home. LONGSHADE_BEDAZZLE_MECHANICS_1
  and EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES wait at machine_load. Six stale blocks are on held mods and read off.
- Context after the group: GO ON was not read; the work is complete.

Next: nothing. The member closes.
