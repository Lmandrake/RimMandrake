# BOUNDARY: one record of who drives each game, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/game_lock.py` (all of it), `src/RimMandrake/rimflow/cli.py` (`lock_reading`, `lock_holder`, `_mirror_bridge`, `_who_lines`, `_bridge_who`, `_lock_view`, `_live_other`, the take, idle and release decisions of `bridge` for ArchBig and for `--host`), `src/RimMandrake/rimflow/host_guard.py` (`acquire`, `crossing`), `src/RimMandrake/rimflow/maturation.py` (`bridge_idle`), `src/RimMandrake/rimflow/maturation_dispatch.py` (`lock_says`, the driven-game line of `pick_game`), `src/RimMandrake/Utils/game_instance.py` (`status_lines`, `_driver`), `src/RimMandrake/rimflow/control.py` (`game_lines`, the game lines of `show` and `why`), `src/RimMandrake/Utils/rmpaths.py` (the data-root cache), `src/RimMandrake/rimflow/model.py` (`game_a_lock_path`,
`game_a_lock_record`, `bridge_gate`), `src/RimMandrake/rimflow/driver_lock.py` (`process_alive` of a WSL holder seen from Windows, `my_identity` of a Windows process, `clone_key`, the `clone` and `role_unit` a take
records), and the ArchBig readers `testq.bridge_holder`, `bridgetools/build.py` `bridge_holder`,
`seat_restart.bridge_reading` and `wrapup.World.game_a_hold`; the readers of who drives each game
`game_lock.query_all` (MATURATION_NOW's games line), `preflight_bridge.c_bridge_lease` (check O02, item
`RIMMANDRAKE_MOVE_GAME_DRIVER_READERS_OFF_BRIDGE_FILE_TWO_LEFT`), `handoff.bridge_lines`
and `FlowWorks/northstar/preflight_flowworks.p_b1` (item `RIMMANDRAKE_MOVE_TWO_MORE_GLANCE_READERS_CENSUS_MISSED`).
Item: `RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_RECORDS_DISAGREE`, written 2026-11-21. The owner, about 3:35 AM PST:
*"We need a lightning responsive deterministic python way of taking and releasing game A or B as well as determining if
it's available or not. Seems like right now it's the Wild West. ... A single point of reference and truth? And most
importantly, a token free lightning fast way to query, claim, and release."* Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_game_lock.py`. This page covers only the parts of the files named above; the rest of
each file has its own page or none.

## The one record, and why it is this one

Who drives game X has one record: that game's process-keyed driver lock. ArchBig's is `<data root>/scratch/
DRIVER_LOCK.json` (`D:\ClaudeWork\rimmandrake\scratch\DRIVER_LOCK.json`); a named game's is `<instances root>/<g>/
DRIVER_LOCK.json`. It was already the only record that every clone, every script and the Windows `python.exe` tools
see at once, and the only one whose holder is a process, so a holder that dies frees the game the moment it dies. The
ledger's bridge events stay, as history written after the act; nothing decides from them where a lock is readable.
The BRIDGE glance file (`infrastructure/state/BRIDGE`) is retired: nothing writes it and nothing reads it. The glance is
`game_lock.py query all`.

Its place stays on the D: drive, by measurement (2026-11-21, Archmagi, WSL, two games running): reading the lock there
takes 2 ms. What made a query slow was not the drive: the data root cost about 110 ms per process (a Python subprocess
of Lodestar's helper, reading `~/dev` on D:), now cached on ext4 (`rmpaths.py`), and `argparse` about 15 ms, which
`query` does not use. Measured after: `game_lock.py query a` 41 ms, `query b` 48 ms, `query all` 51 ms (median of 9).
Before: `rimflow bridge who` 5.0 s for ArchBig, 1.8 s for ArchSmall.

## ACCEPTS (the only inputs this is built for)

- **a-game-letter.** `a`, or a named game (`b`, ...) of `game_instance.instances()`. `all` for a query.
- **a-lock-in-driver-locks-shape.** `{seat, purpose, identity: {pid, start, boot_id, platform, host}, acquired,
  heartbeat, generation, clone, role_unit}`, as `driver_lock.acquire` writes it (`clone` and `role_unit` since
  2026-11-21; a lock without them reads the same, with no clone to attribute). Every old door writes this shape.
- **a-process-tree.** The holder of a `claim` is the nearest `claude` or `codex` ancestor (the window or the run), or
  `RM_DRIVER_PID`; of a `run`, the `game_lock.py` process itself. "This process tree" is the caller and its ancestors.
- **the-control-store.** `control.py`'s store, for `pipe off game:<g>`. A store that does not exist holds nothing.
- **redirected-paths-in-tests.** `RIMFLOW_DRIVER_LOCK` (ArchBig, or the game `RM_GAME_INSTANCE` names),
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
- **two-drivers-in-one-clone-from-windows.** A Windows `python.exe` cannot see its WSL ancestors, so one running the
  holder's own clone's code passes `host_guard.crossing` without a take of its own. From another clone it is refused.
- **a-wsl-holder-whose-distro-is-unknown-from-windows.** A Windows `python.exe` reads a WSL holder's process through
  `\\wsl.localhost\<distro>\proc`. With no distro on the lock, in its own code path or in `WSL_DISTRO_NAME`, the
  heartbeat decides (45 min).
- **a-machine-with-no-lock-readable.** Another machine's game (SteveDesktop's, from Archmagi) is read through its guard
  over ssh, or its test lane. A clone with no lock path (a test ledger) prints the ledger's history, said to be history.

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
  or is stopped by a SIGTERM forwarded to it; a child of `run` reads the hold as its own tree's, and its driver-lock owner
  (`RM_DRIVER_PID`) is the run, so `game_instance.stop`'s gate passes CMD's own hold; a `run` killed outright leaves the
  game FREE at once.
- **his-hold-refuses-with-exit-3.** `pipe off game:<g>`, his OWNER lock (live, or with its process gone, which a query
  cannot measure), and a flyer's flight each make `query` or `claim` exit 3 by name. His own claim for a flight passes.
  `claim --despite-hold WHY` with a nonempty reason passes the pipe hold, reports the hold and the reason on stderr,
  and leaves the switch set. A successful claim still records the driver for `query` to name. Another live driver's
  lock, his OWNER lock, and an unreadable control store still refuse the claim.
- **an-old-style-hold-is-seen-and-an-old-style-release-frees-it.** A take made through `host_guard.py take` or
  `driver_lock.acquire` (what `rimflow bridge take` calls) reads HELD with its purpose; `host_guard.py release` frees it;
  `host_guard.py status` reads a claim made here.
- **release-frees-only-this-process-trees-hold.** `release` of another tree's live hold exits 75 and touches nothing;
  `--force "<why>"` cuts it; the holder or a child of it releases its own; a free game reads `already FREE`, exit 0.
- **a-query-answers-under-100-ms.** On quiet WSL, `game_lock.py query a` takes under 100 ms as a fresh command.
  The selftest prints the median and worst wall time of nine calls against a throwaway held lock and control store.
  The wall bound is UNMEASURED when the one-minute load exceeds half the available CPUs or the median of nine
  interleaved bare Python starts exceeds 30 ms (twice the upper end of the 12-15 ms bare Python CPU reading on
  Archmagi, 2026-11-24). Guest CPU time also rose to 103-118 ms per query in three failed runs at load 38-48.
  On every run, fresh queries on a warm data-root cache with a free lock, a live holder, and a pipe hold must answer
  with no process starts, network connections, sleeps, unapproved imports or extra file opens or database connections.
  Those three fixtures also permit up to 850 executed repository line events per query (771 measured on 2026-11-24,
  with room for small changes). The test prints the worst count, limit and case count. These checks decide on busy WSL.
- **the-225-am-release-that-left-bridge-who-saying-held.** When a run's holder process has ended with its take still in
  this clone's ledger, `rimflow bridge who` reads FREE and the next `rimflow bridge take` succeeds without `--force`.
  A take still honours his `pipe off game:<g>`, and a control store that cannot be read refuses it as COULD NOT LOOK
  (`selftest_bridge_take_pipe_hold.py`).
- **the-243-am-game-b-record-that-named-the-ended-run.** `rimflow bridge who --host ArchSmall` names ArchSmall's live holder
  from its lock, never a run that has ended.
- **the-335-am-ledger-free-while-the-lock-was-held.** With this clone's ledger empty and another clone's live hold in the
  lock, `rimflow bridge who` reads HELD, no BRIDGE glance file is written, a take from this clone exits 75, and a
  release from it frees nothing and exits 75.
- **the-tick-line-that-named-a-dead-run-as-live.** The tick's line about a game a run record names carries the lock's
  reading at that moment; its free-game reading (`maturation.bridge_idle`) is the lock's: HELD while a holder lives,
  free the moment it is gone, never for a flyer's flight.

- **the-old-shared-file-is-neither-written-nor-read.** A take or release writes no `BRIDGE_SHARED.json`, and one left
  on disk names no holder anywhere. `model.bridge_gate`, `testq`, `seat_restart` and `wrapup` name ArchBig's holder from
  its lock, with the unit and clone that took it, and read it free the moment its process is gone.

- **a-windows-python-client-obeys-the-lock.** A Windows `python.exe` bridge client (`host_guard.crossing`, which
  `rimbridge_client` asks before each mutating call) is refused while another clone's live process holds the game. It
  passes when it inherited the take (`RM_HOST_GUARD_GEN`, which `game_lock.py run` exports through `WSLENV`), when it
  runs the holder's own clone's code, or when the holder is gone. From Windows, a WSL holder is judged by its process
  (pid, start time, boot), not by its heartbeat: one that died reads gone at once, and one that holds past 45 min stays
  held. The test runs the real `python.exe` and reads UNMEASURED where there is none.

- **a-windows-python-client-checks-the-lock-in-under-50-ms.** Under a live WSL holder, a Windows `python.exe` bridge
  client's own steps for one mutating call (the lock check, the in-flight marker and evidence rows, with no game) take
  under 50 ms a call on average. The client reads its own Windows start time once per process, never once per call.
  The test runs the real `python.exe` (`selftest_game_lock_windows_python.py timed`) and reads UNMEASURED where there is none.
  The timed calls start no process (counted at `subprocess.Popen`; a per-call spawn was the 233 ms defect), on every
  run. When the load average passes half the cores, a wall reading over 50 ms is printed UNMEASURED and the spawn count
  decides (measured 2026-11-21: 36-43 ms quiet; 109-130 ms inside `./publish`'s side-by-side door tests).

- **the-two-last-glance-file-readers-read-every-game-from-the-lock.** `preflight_bridge.c_bridge_lease` reads the lock
  of its own process's game (`RM_GAME_INSTANCE`, ArchBig by default) and `game_lock.query_all` reads every game
  of this machine, each through `game_lock.query`; neither opens the BRIDGE glance file. With no glance file anywhere,
  a held ArchBig and a free ArchSmall read as `game_lock.py query all` reads them. An unreadable lock reads UNMEASURED
  by its cause, never FREE and never held. A free game under `pipe off game:<g>` is his hold, never FREE. The
  equivalence run `selftest_game_driver_readers.py` compares the old readers (frozen copies, fed the glance file that
  a frozen copy of the retired printer writes from the same lock) with the new on fixture cases, and with `--recorded`
  on every lock kept on this machine. Measured 2026-11-22: 227 kept locks and 4 clone glance files, no unclassed
  difference; 8 planted faults in the new readers, 8 caught.

- **the-handoff-and-flowworks-p-b1-read-the-lock-and-nothing-prints-a-glance-file.** The handoff's `- Bridge:` lines
  (`handoff.bridge_lines`) are `game_lock.query_all`'s lines, one per game; a lock that cannot be read is its game's
  COULD NOT LOOK line, never `unknown` and never FREE. FlowWorks's P-B1 (`preflight_flowworks.p_b1`) PASSes only when
  this seat or this process tree holds the lock of its own process's game, read with `game_lock.query(pipe=False)`
  (his `pipe off` is O02's question, not P-B1's); a holder whose process is gone holds nothing; an unreadable lock is
  UNMEASURED. Neither opens a BRIDGE glance file, and `rimflow` has no printer of one (`cli._mirror_bridge`,
  `model.write_bridge_file` are gone). The same equivalence run covers both (item
  `RIMMANDRAKE_MOVE_TWO_MORE_GLANCE_READERS_CENSUS_MISSED`). Measured 2026-11-22: red on 2d45788d5c (16 FAIL); green
  after; `--recorded` 227 kept locks, 3719 reader verdicts, no unclassed difference; 9 planted faults in the two new
  readers, 9 caught (`glance_reader_mutations.py` beside this page).

Later lists beside this page: `polish.md`, `next_version.md`.
