# BOUNDARY — deploy-update installs the unit texts that drifted

Code: `src/RimMandrake/Utils/ops_core/deploy_update.py` (`install_units`, its call in `main`, and the
`src/RimMandrake/Utils/systemd` entry of `SPARSE_DIRS`).
Tests: `src/RimMandrake/Utils/ops_core/selftest_deploy_installs_units.py`.
Item: `RIMMANDRAKE_INSTALL_UNIT_TEXTS_ON_DEPLOY_NOT_BY_HAND`. The one home of unit texts and the only installer
(`ops_clocks.py install`) are on `design/specs/2026-11-22-units-one-folder/boundary.md`; this page adds who calls it.

## Why

A unit text that landed in `src/RimMandrake/Utils/systemd/` reached `~/.config/systemd/user` only when an agent ran
`ops_clocks.py install` by hand. The deadman's units arm (`LIVE_RESTORE_UNITS`) went red three times on
2026-11-23 and 2026-11-24 for that drift. Each `rm-deploy-update` pass (every 10 min) now installs the drift from the
deploy checkout, which is origin/main.

## ACCEPTS

- The deploy checkout `/home/mandrake/rm/pulse-deploy` after a good pull, with `src/RimMandrake/Utils/systemd` in its
  sparse cone. The first pass of new code sets the cone; the next pass installs.
- An install dir that holds our units, the owner's other units and masked (retired) names.

## DOES NOT SURVIVE

- A pass whose git timed out (a skip) installs nothing; the next good pass does.
- A changed text of a running service takes effect at that unit's next own start. Nothing restarts it.
- A masked drop-in under a unit whose service or timer drifted makes `ops_clocks.py install` refuse the pass, and the
  unit fails loudly.

## PROMISES

- **the-deploy-holds-the-unit-folder.** `SPARSE_DIRS` holds `src/RimMandrake/Utils/systemd`.
- **a-drifted-text-is-installed-with-one-reload-and-no-start.** Every folder file whose installed copy differs or is
  absent is written; the only systemctl call is one `daemon-reload`. No unit is enabled, started or restarted,
  because a unit may launch Claude.
- **no-drift-touches-nothing.** When nothing differs, nothing is written and systemctl is not called.
- **a-mask-is-skipped-and-the-rest-still-installs.** A masked name stays a mask and is reported; the other files
  still install.
- **a-missing-folder-or-failed-reload-fails-loudly.** A missing unit folder or a failed reload raises, so the unit
  fails and `TIMER_FAILED` sees it.
- **main-installs-after-a-good-pull-and-not-after-a-skip.** `main` installs after a good pull and prints
  `deploy update: units: wrote N (...)`; a skipped pass installs nothing.
