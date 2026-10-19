# DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO — regenerate every def still wearing borrowed art

Filed 2026-10-18 by a FOUNDRY helper on the owner's question *"Any art recommissioning we can get going now in the
background that still wears Donor art?"*, under the no-donor-art ruling (2026-10-05, vanilla counts as donor) and
the accept-for-now ruling (*"Simply accept all art as currently rendered to get this done. We will re review at a
later time. No more art blockers."*). Record: `design/RimMandrake/donor_art_census_2026-10-18.md` §3.5.

## spec

- Job list `design/RimMandrake/donor_regen_jobs_2026-10-18.json` (457 defs, 627 rows, 765 job files), built by
  `src/RimMandrake/Utils/art/donor_regen_jobs.py build` from a fresh census + `texture_regen_audit.py`.
- Fed by `donor_regen_jobs.py submit --cap 40` (transient timer `rm-donor-regen-feeder.timer`, every 10 min). Order:
  start-region creatures, other creatures, plants, terrain, buildings, items, icons.
- Renders land in `D:\Luke\dev\_artpipe\done`; installing them is `REGEN_RENDERS_INSTALL_AS_THEY_LAND`.

## verify

- `python3 src/RimMandrake/Utils/art/donor_regen_jobs.py submit --jobs design/RimMandrake/donor_regen_jobs_2026-10-18.json --dry-run`
  prints "every row already filed".
- `ls D:\Luke\dev\_artpipe\done\dregen_*.manifest.json` count vs `failed\dregen_*`: failures retried or listed.
- Then stop the timer: `systemctl --user stop rm-donor-regen-feeder.timer`.

## hourly install (2026-10-19)

Owner decision, by question card 2026-10-19: finished donor-replacement renders are installed AUTOMATICALLY EVERY HOUR.
Timer `rm-donor-regen-install.timer` (transient `systemd-run --user --on-calendar=hourly`) runs
`src/RimMandrake/Utils/art/donor_regen_install_hourly.py` (`--dry-run` supported; log `Transient/donor_regen_install.log`):
`art_accept_finished.py --prefix dregen_ --apply`, then commits only the run's installed/repointed paths + the FOUNDRY art-events shard, then `./publish`.
Skips on an index lock; a refused push is logged and retried next hour. Owner-KEPT pictures stay refused (need his words).
Like the feeder it is transient and DIES ON WSL RESTART: re-create it with the same `systemd-run` line.
