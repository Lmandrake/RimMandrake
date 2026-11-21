# BOUNDARY: one record of who drives each game, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/game_lock.py` (all of it), `src/RimMandrake/rimflow/cli.py` (`lock_reading`, `lock_holder`, `_mirror_bridge`, `_who_lines`, `_bridge_who`, `_lock_view`, `_live_other`, the take, idle and release decisions of `bridge` for game a and for `--host`), `src/RimMandrake/rimflow/host_guard.py` (`acquire`), `src/RimMandrake/rimflow/maturation.py` (`bridge_idle`), `src/RimMandrake/rimflow/maturation_dispatch.py` (`lock_says`, the driven-game line of `pick_game`), `src/RimMandrake/Utils/game_instance.py` (`status_lines`, `_driver`), `src/RimMandrake/rimflow/control.py` (`game_lines`, the game lines of `show` and `why`), `src/RimMandrake/Utils/rmpaths.py` (the data-root cache).
Item: `RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_RECORDS_DISAGREE`, written 2026-11-21. The owner, about 3:35 AM PST:
*"We need a lightning responsive deterministic python way of taking and releasing game A or B as well as determining if
it's available or not. Seems like right now it's the Wild West. ... A single point of reference and truth? And most
importantly, a token free lightning fast way to query, claim, and release."* Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_game_lock.py`. This page covers only the parts of the files named above; the rest of
each file has its own page or none.

## The one record, and why it is this one

Who drives game X has one record: that game's process-keyed driver lock. Game a's is `<data root>/scratch/
DRIVER_LOCK.json` (`D:\ClaudeWork\rimmandrake\scratch\DRIVER_LOCK.json`); a named game's is `<instances root>/<g>/
DRIVER_LOCK.json`. It was already the only record that every clone, every script and the Windows `python.exe` tools
see at once, and the only one whose holder is a process, so a holder that dies frees the game the moment it dies. The
ledger's bridge events stay, as history written after the act; nothing decides from them where a lock is readable.
The BRIDGE glance file is printed from the lock.

Its place stays on the D: drive, by measurement (2026-11-21, Archmagi, WSL, two games running): reading the lock there
takes 2 ms. What made a query slow was not the drive: the data root cost about 110 ms per process (a Python subprocess
of Lodestar's helper, reading `~/dev` on D:), now cached on ext4 (`rmpaths.py`), and `argparse` about 15 ms, which
`query` does not use. Measured after: `game_lock.py query a` 41 ms, `query b` 48 ms, `query all` 51 ms (median of 9).
Before: `rimflow bridge who` 5.0 s for game a, 1.8 s for game b.

## ACCEPTS (the only inputs this is built for)

- **a-game-letter.** `a`, or a named game (`b`, ...) of `game_instance.instances()`. `all` for a query.
- **a-lock-in-driver-locks-shape.** `{seat, purpose, identity: {pid, start, boot_id, platform, host}, acquired,
  heartbeat, generation}`, as `driver_lock.acquire` writes it. Every old door writes this shape.
- **a-process-tree.** The holder of a `claim` is the nearest `claude` or `codex` ancestor (the window or the run), or
  `RM_DRIVER_PID`; of a `run`, the `game_lock.py` process itself. "This process tree" is the caller and its ancestors.
- **the-control-store.** `control.py`'s store, for `pipe off game:<g>`. A store that does not exist holds nothing.
- **redirected-paths-in-tests.** `RIMFLOW_DRIVER_LOCK` (game a, or the game `RM_GAME_INSTANCE` names),
  `RM_INSTANCES_ROOT` (named games), `RM_CONTROL_DB`. Under `RIMFLOW_LEDGER` without them there is no lock path.

## DOES NOT SURVIVE (not promised)

- **a-windows-holder-queried-from-wsl.** A query does not inspect a Windows `python.exe` holder (a PowerShell probe costs
  about 1 s): its heartbeat decides, up to 45 min. A `claim` inspects it.
- **a-holder-on-another-machine.** Its pid means nothing here; its heartbeat decides (45 min), as `driver_lock` does.
- **sigkill-of-run.** The game reads FREE at once, but CMD keeps running, orphaned.
- **an-owner-handover-by-bridge-give.** `./bridge conductor` frees the lock and writes history; the Conductor's next take
  claims it. Until then the game reads FREE.
- **a-driver-that-never-claims.** A tool that drives the game without a claim is guarded only where `host_guard.crossing`
  runs (every mutating `rimbridge_client` call).
- **a-machine-with-no-lock-readable.** Another machine's game (SteveDesktop's, from Archmagi) is read through its guard
  over ssh, or its test lane. A clone with no lock path (a test ledger) prints the ledger's history, said to be history.
- **the-shared-file-and-its-older-readers.** `BRIDGE_SHARED.json` is still written by `bridge take` and `release`, and read
  by `testq`, `bridgetools/build.py`, `seat_restart`, `wrapup` and `model.bridge_gate`. No door named on this page decides
  from it. Its retirement is open on the item.

## PROMISES (each one is owed a test of the same name)

- **one-record-per-game.** A claim of game g writes only g's lock: no ledger event, no other game's lock. `query`,
  `claim` and `release` use no ledger replay, no git, no model and no network for this machine's games.
- **two-claimers-race-and-exactly-one-wins.** Of claimers that start together, one exits 0 and the lock names it; every
  other exits 75.
- **a-dead-holder-reads-free-at-once.** When the holder process is gone, `query` exits 0 FREE and names the gone holder,
  and the next `claim` takes the game without `--force`.
- **an-unreadable-lock-is-could-not-look.** A garbled lock, a lock that stays empty, no lock path, or a control store that
  cannot be read: `query`, `claim` and `release` exit 2 and name the cause. It is never read as free or as held.
- **run-releases-on-exit-crash-and-sigterm.** `run` returns CMD's exit code and the lock is gone after CMD exits, crashes
  or is stopped by a SIGTERM forwarded to it; a child of `run` reads the hold as its own tree's; a `run` killed outright
  leaves the game FREE at once.
- **his-hold-refuses-with-exit-3.** `pipe off game:<g>`, his OWNER lock (live, or with its process gone, which a query
  cannot measure), and a flyer's flight each make `query` or `claim` exit 3 by name. His own claim for a flight passes.
- **an-old-style-hold-is-seen-and-an-old-style-release-frees-it.** A take made through `host_guard.py take` or
  `driver_lock.acquire` (what `rimflow bridge take` calls) reads HELD with its purpose; `host_guard.py release` frees it;
  `host_guard.py status` reads a claim made here.
- **release-frees-only-this-process-trees-hold.** `release` of another tree's live hold exits 75 and touches nothing;
  `--force "<why>"` cuts it; the holder or a child of it releases its own; a free game reads `already FREE`, exit 0.
- **a-query-answers-under-100-ms.** `game_lock.py query a`, run as a fresh process from WSL on the live locks (read
  only), takes under 100 ms, median of 9, in one of up to three batches; the test prints every batch, its CPU time and
  the load. When the load average passes half the cores the wall bound is printed UNMEASURED and the CPU time per query
  decides (measured 2026-11-21: 38-45 ms wall and 33 ms CPU quiet; 110-274 ms wall and 63-72 ms CPU inside
  `./publish`'s side-by-side door tests).
- **the-225-am-release-that-left-bridge-who-saying-held.** When a run's holder process has ended with its take still in
  this clone's ledger, `rimflow bridge who` reads FREE and the next `rimflow bridge take` succeeds without `--force`,
  even with a control store that cannot be read (his pipe hold binds pipeline runs, not a window's take).
- **the-243-am-game-b-record-that-named-the-ended-run.** `rimflow bridge who --host archmagi.b` names game b's live holder
  from its lock, never a run that has ended.
- **the-335-am-ledger-free-while-the-lock-was-held.** With this clone's ledger empty and another clone's live hold in the
  lock, `rimflow bridge who` reads HELD, the BRIDGE glance file says HELD, a take from this clone exits 75, and a
  release from it frees nothing and exits 75.
- **the-tick-line-that-named-a-dead-run-as-live.** The tick's line about a game a run record names carries the lock's
  reading at that moment; its free-game reading (`maturation.bridge_idle`) is the lock's: HELD while a holder lives,
  free the moment it is gone, never for a flyer's flight.

Later lists beside this page: `polish.md`, `next_version.md`.
