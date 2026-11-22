# BOUNDARY: every systemd unit text has one home, Design Version 0.1.0

Code: `src/RimMandrake/Utils/ops_clocks.py` (`folder_units`, `installed_units`, `judge_units`, `embedded_units`,
`embedded_in_tree`, `units_problems`, `install`, the `units` and `install` commands and the units clause of `check`),
`src/RimMandrake/Utils/deadman_check.py` (`units_arm`), and the folder `src/RimMandrake/Utils/systemd/` itself.
Item: `RIMMANDRAKE_MOVE_UNIT_DEFINITIONS_INTO_ONE_FOLDER_SOME_LIVE_ONLY_ON_MACHINE`, group 7 of
`design/specs/2026-11-22-pipeline-single-source-sweep/report.md` (candidate 8). Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_units_one_folder.py`. This page covers only the parts named above; the clock and deploy
judgment of `ops_clocks.py check` is older and keeps its own tests (`selftest_ops_clocks_check.py`).

## The one home, and why it is this one

The text of every `rm-*`, `testq-*`, `timer-guard`, `account-plan`, `steve-cpu-retest` and `claude-seats` unit, and of
each drop-in under one of them, is one file in `src/RimMandrake/Utils/systemd/`, with the name it has when installed
(`rm-deadman.timer`, `rm-memwatch.service.d/rm-data-root.conf`). The file is the literal text systemd reads: no
template, no `{deploy}`. The deploy that clocks run from is written in the file, and `check` judges it against
`ops_clocks.json`'s deploy, as before. The only installer is `ops_clocks.py install`. No Python source holds unit text.

Before 2026-11-22, seven installers held 18 unit texts in Python strings (`deadman_check`, `timers_guard`, `ops_watch`,
`account_usage`, `switching_plan`, `testq`, `steve_cpu_retest`), 10 drop-ins and 10 of those units lived only on
Archmagi, and unit files sat in three `systemd/` folders and loose in `Utils/`. Nothing compared any of them with what
was installed, so nothing could see drift.

## ACCEPTS (the only inputs this is built for)

- **a-unit-folder.** A directory of unit files (`*.service`, `*.timer`, `*.path`, `*.slice`, `*.socket`, `*.target`)
  and drop-in directories `<unit>.d/*.conf`. Other files there (`ops_clocks.json`, `metronome_phases.json`,
  `90-rm-order7.conf`) are not units and are not judged.
- **an-install-dir.** `~/.config/systemd/user` (`RM_UNIT_INSTALL_DIR` overrides it, tests only). Only names that match
  `INSTALL_GLOBS` are judged; the owner's other units there (hestia, lodestar, augur) are not ours.
- **a-source-tree.** The `.py` files under `src/RimMandrake/`. A file whose name starts `selftest_` or `test_`, or that
  lies under a `tests/` directory, may hold unit text as a fixture.

## DOES NOT SURVIVE (not promised)

- **another-machine.** SteveDesktop's units (`infrastructure/stevedesktop/`) are not judged from Archmagi. On a machine
  with no install dir, the units clause says it could not look; it never reports every folder file missing.
- **a-unit-in-a-system-wide-dir.** Only the user install dir is read; `/etc/systemd/user` is not.
- **a-transient-unit.** `systemd-run` units (`rm-role-*`, `rm-detached-*`, `timer-resume-*`) have no file in the
  install dir, so there is nothing to judge.
- **a-runtime-drop-in-written-by-a-tool.** `control.py install_dropin` writes `50-rm-control-permit.conf` with the
  store's permit path. The two live ones are in the folder as their literal text; a store moved elsewhere makes them
  differ, and `check` says so.

## PROMISES (each one is owed a test of the same name)

- **a-unit-installed-only-here-is-named.** An installed unit or drop-in in scope with no folder file of its name is a
  problem: "lives only on this machine".
- **an-installed-text-that-differs-is-named.** A folder file whose installed copy differs by any byte (a changed
  `OnCalendar` included) is a problem that names the install command that repairs it.
- **a-folder-unit-not-installed-is-named.** A folder file with no installed copy is a problem.
- **a-mask-is-not-a-definition.** An installed name that is a symlink to `/dev/null` (a retired unit,
  `retired_loops_check.py` keeps it) is not judged as text; a folder file for a masked name is a problem, because the
  copy is dead.
- **embedded-unit-text-in-code-is-red.** A non-test Python source with a string that holds a `[Service]`, `[Timer]`,
  `[Path]`, `[Slice]` or `[Socket]` section line is a problem naming the file and line. A test file may hold one.
- **an-unreadable-install-dir-is-could-not-look.** An install dir that is missing or cannot be read gives one problem
  that says so, not a line per unit.
- **install-writes-only-what-differs-and-never-over-a-mask.** `install` without `--apply` writes nothing and prints
  `write` or `unchanged` per file; with `--apply` it writes the files that differ, then reloads systemd once; it
  refuses a name that is masked or not in the folder; `--enable` enables and starts only the named triggers.
- **every-folder-clock-runs-from-the-deploy.** Each clock's folder `.service` passes the deploy judgment of `check`
  against the deploy in `ops_clocks.json`.
- **test-throwaway-units-are-not-judged.** Names a selftest creates and removes in the real install dir
  (`testq-selftestthrow-*`, `rm-probe-*`) are skipped, so a test that runs during a pass does not alarm.
- **deadman-rechecks-units-every-pass.** `deadman_check.py run` runs the units clause as arm `units` on every pass: a
  problem files the one fixed item `LIVE_RESTORE_UNITS`, and the reading `ops_watch/units.json` is rewritten each pass.
