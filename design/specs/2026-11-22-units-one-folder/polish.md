# Polish: units in one folder (a record; nobody takes lines from it)

- `steve-cpu-retest.timer` ticks every 60 s on Archmagi, but its controller has sat in the final state `END_FAULT` since
  its last run; each tick only reads the state. Retiring the timer is a call for whoever owns the SteveDesktop lane.
- `steve_cpu_retest.py install-timer` copies the script to `STEVE_RETEST_HOME`, but the folder unit names the default
  home. A run with that variable set installs a unit that runs an older copy.
- `control.py install_dropin` is a second writer of the `50-rm-control-permit.conf` drop-ins whose live copies are now
  in the folder. `selftest_control.py` once left an `rm-probe-r4ghost2913433-.service.d` drop-in in the real install dir
  (deleted 2026-11-22). The report already lists `install_dropin` as dead code.
- `selftest_timers_guard.py` writes `testq-selftestthrow-<pid>` units into the real install dir and removes them in
  `finally`; a killed run left one pair from 2026-11-06 (deleted 2026-11-22). The units check skips that name.
- `run_selftests.py` and `claude_bounded.sh` each install their slice when the file differs. A clone that has not
  pulled a changed slice installs the old text again, so `units` reads red until a current clone runs. The slices'
  text was kept byte-identical in this move for that reason.
- The 13 masks the report proposed to delete stay: `retired_loops_check.py` requires them (and the retired eras index
  says the masks stay). A mask is not a unit definition; the units check skips it.
- `design/RimMandrake/dispatcher_golive_wave1.md` still quotes `src/RimMandrake/rimflow/systemd/rm-dispatcher.service`
  in its dated command lines. It is a record of what was run on that day.
