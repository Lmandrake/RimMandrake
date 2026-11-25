# BOUNDARY: ./publish's door checks queue for a per-machine slot, Design Version 0.1.0

Code: `src/RimMandrake/Utils/treecheck_slots.py` (`Gate`), used by `src/RimMandrake/Utils/publish.py` (`_publish`,
`tree_checks`, `pipeline_checks`). Item: `RIMMANDRAKE_THROTTLE_TREECHECKS_WHEN_DISK_SATURATES_HANG_GUARDS_FIRE`,
written 2026-11-24. On SteveDesktop, 2026-11-24 5:49 PM to 9:41 PM PST, nine detached runs each ended with `./publish`.
Up to six door checks ran at once on one disk: the disk read 100% busy, load reached 47, one publish was starved for
148 minutes, and hang guards fired on healthy git calls. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_treecheck_slots.py`.

## ACCEPTS (the only inputs this is built for)

- **publishers-on-one-machine.** Any number of `./publish` processes, from any clones, that share one `RM_ROOT`
  (`PUBLISH_RM_ROOT`, default `/home/mandrake/rm`). The gate lives in `RM_ROOT/.treecheck-slots/`. Two machines never
  share a gate.
- **a-filesystem-with-flock.** The gate directory is on a local filesystem where `flock` works (ext4 here).

## DOES NOT SURVIVE (not promised)

- **a-holder-that-hangs-inside-its-checks.** A holder keeps its slot while it lives. The bounds on its own work end
  it: `CHECKTREE_GIT_TIMEOUT_S` for the checkout git calls, `progress_guard` and `CHECK_CAP_S` for each check. The gate
  adds no wall limit of its own.
- **orphaned-check-children.** The slot is the publisher's flock. When a publisher is killed while its check children
  live on, the slot frees, and the next publisher starts beside the orphans.
- **a-gate-directory-that-cannot-be-opened.** Then the publish says so in one line and runs its checks without the
  gate, as before this page. Could not look is not a refusal.
- **other-disk-load.** The gate counts only door checks. The pool monitor's `find` scans, builds and live games are
  not in it.

## PROMISES (each one is owed a test of the same name)

- **at-most-the-limit-run-at-once.** When more publishes than the limit reach their door checks on one machine, at most
  the limit run their full checkout and checks at the same time. The rest wait, and every one of them finishes.
- **waiters-go-first-come-first-served.** Publishes that wait take the free slots in the order in which they began to
  wait.
- **a-dead-holder-frees-its-slot.** A slot is a lock held by a live process, not a file. When a holder dies (killed,
  `SIGKILL` included), the next waiter takes the slot at once. A waiter that dies leaves the line, and the waiters
  behind it move up.
- **a-waiter-shows-progress.** A publish that must wait says so at once, and again every `SAY_S` seconds, on stderr:
  `waiting <s> s for a tree-check slot, <N> ahead, <K> running (<holders>)`. So a guard on progress never reads the
  wait as a hang.
- **one-publish-holds-one-slot-across-both-checks.** A publish that runs the whole-tree checks and then the pipeline
  checks holds one slot for both. It does not join the back of the line between them.
- **a-check-under-a-held-slot-never-waits-again.** A process started inside a held slot (a door check that itself runs
  a fixture publish) passes the gate at once. So no set of holders can wait on each other.
- **a-publish-with-no-door-checks-takes-no-slot.** A publish whose change runs no door checks (only `skip_when_only`
  paths, no pipeline test touched) neither waits nor takes a slot.

## LIMITS

- **`SLOTS = 2`** (`RM_TREECHECK_SLOTS` sets another number for one machine). Danger: the 2026-11-24 SteveDesktop
  failure above. Evidence, measured on Archmagi 2026-11-24 9:47 to 10:01 PM PST at load 10 to 15
  (`evidence/measure_archmagi.jsonl`, made by `evidence/measure.py`): one door check run (full checkout and the 23
  checks) took 50 s alone. With 2, 4, 6 and 8 started at once, each took 44, 82, 133 and 179 s. So the machine's
  throughput is the same from 2 up (about 22 s of wall per run), and each run past 2 only adds wait and load (load 34 at
  4, 68 at 8). SteveDesktop was not measured: its disk was saturated by live runs, and a measurement there would have
  slowed them.
- **`SAY_S = 30`**. Not a limit: the interval of the waiting line. The wait goes on.
- **The wait itself has no limit.** It is a guard on progress: the line moves while the holders live, and each holder's
  work is bounded by the limits named above.

## PROOF

- 2026-11-24 10:28 PM PST, Archmagi: four `./publish` runs of trivial commits, from four scratch clones, started at
  once (`evidence/proof4.py`, timeline in `evidence/proof4.json`). All four printed `PUBLISHED`. At most 2 of them held a
  check tree at the same time, and at most 2 slots were locked (`/proc/locks`). The two that waited printed the waiting
  line at 0 s and 30 s, and took a slot after 51 s and 52 s.
- The selftest was red on the code before the gate (`evidence/selftest_red_old_publish.txt`: 4 probes at once) and
  caught 4 of 4 plants (`evidence/selftest_mutants.txt`).
