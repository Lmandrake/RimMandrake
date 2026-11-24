# BOUNDARY: a timed unit's heavy git children run in their own cgroup, Design Version 0.2.0

Code: `src/RimMandrake/rimflow/own_cgroup.py`; its callers `detached_helper.take_clone`,
`maturation_dispatch.land_spend`, `maturation._git_log`, `maturation_rescue.read_nudges`, `build_match.source_sha` and
`testq/ingest.rimflow`. Item `RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN`.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_own_cgroup.py`. The live outcome check is
`src/RimMandrake/rimflow/acceptance/tick_peak_accept.py`.

Measured 2026-11-24: 9 of 11 ticks that launched a run reached the unit's 1G MemoryMax, with swap, and took 2 min 28 s
to 11 min 21 s; a launch checks a run's clone out (about 4 GB of files) as a child in the tick's cgroup. In a bench, a
`git clone --shared` and `read-tree` under a 340 MB parent in a 1G scope peaked at 1024 MB with 22,000 to 26,000
limit hits; with the same children in their own scope the parent's scope peaked at 343 MB with none. A landing's
`seat_sync.py` child read 169 MB in the live cgroup.

Measured 2026-11-24 6:49 AM to 12:05 PM PST, with the two above in place: 40 of 214 ticks still reached 1000 MB. A git
history read of one mod maps 350 to 970 MB of the clone's 10.6 GB pack, charged to the tick (a cold read in its own
scope: `log --name-only` of the whole history 974 MB, `log -p` of fourteen days 351 to 651 MB, `log -1` about 118 MB),
and the reclaim swapped the tick's own pages (up to 165 MB). A launch's `cli.py spawn` held 400 MB beside the tick's
361 MB. A cold dry tick in a 4G service peaked at 623 MB before this change, 539 and 517 MB after it.

## ACCEPTS (the only inputs this is built for)

- **a-command-run-to-its-end.** The caller waits for the command (`subprocess.run` keywords pass through). A command
  that starts background work is not built for: that work ends with its scope's bound unit.

## DOES NOT SURVIVE (not handled)

- **a-caller-outside-a-service.** In a seat scope or a shell the command runs plainly, in the caller's own cgroup.
- **a-runaway-in-the-child.** A child over MEMORY_MAX is killed by the kernel and the launch fails, as any failed
  clone does; the next tick tries again.

## PROMISES (each one is owed a test of the same name)

- **child-leaves-the-service-cgroup.** Called from a user service, `run` puts the command in a transient scope that is
  not the service's cgroup, and its exit code, output, cwd and environment come back as `subprocess.run` gives them.
- **child-dies-with-its-service.** The scope is bound to the calling service: a service that is stopped takes the
  scope with it, as the service's own cgroup did.
- **outside-a-service-runs-plain.** A caller that is in no user service, or a machine with no systemd-run, runs the
  command as given.
- **scope-refused-runs-plain.** When systemd-run cannot start the scope, the command still runs once, in place; a
  command that ran and failed is never run twice.
- **clone-and-landing-children-use-it.** `take_clone` (a sync and a new clone) and `land_spend` go through `run`; a
  test's own runner is used as given.
- **history-reads-and-the-filing-use-it.** `_git_log`, `read_nudges`, `source_sha` and the ledger write of `ingest.rimflow`
  go through `run`; `_git_log` names `--since` to git, so git does not walk older history, and its answer stays that of a
  whole walk when a commit's clock is up to a day back. A test's own runner is used as given.
