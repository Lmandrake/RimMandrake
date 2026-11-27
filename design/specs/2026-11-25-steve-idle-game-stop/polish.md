# Polish beside the idle-stop page

One line per finding. No line here is a ticket. The next Work Bundle that changes the named file takes the line.

- `src/RimMandrake/Utils/pipeline_tests.json`: the row of `selftest_idle_stop.py` names neither
  `infrastructure/stevedesktop/rw_game.sh` in `inputs` nor any `pipeline_files` glob that matches it, and
  `t_the_lanes_own_guard_does_not_refuse_its_stop` runs that script's real `down`. risk: an edit to only the guard block
  of `rw_game.sh` (lines 238-243) lands with no run of this test at `./publish`, and the idle stop is refused again with
  no red at the door (the 7-refusal fault of 2026-11-26).
