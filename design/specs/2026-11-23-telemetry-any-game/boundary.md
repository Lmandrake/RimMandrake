# BOUNDARY: telemetry takes a game name, Design Version 0.1.0

Code: `src/RimMandrake/Utils/telemetry/games.py`, `pull_games.py` and `games_serve.py` (all of each), and the parts of
`ingest.py`, `store.py`, `analysis.py`, `telemetryd.py` and `cli.py` there that name a game, `process_pids` in `host.py`,
and `game_record` in `src/RimMandrake/Utils/tps_record.py`. Item:
`RIMMASTER_WIRE_STEVEDESKTOP_TELEMETRY_FLYING_BLIND`. Each promise has a test of its name in
`src/RimMandrake/Utils/telemetry/selftest_telemetry_games.py`. The rest of those files has its own tests
(`selftest_telemetry.py`) and no page.

What was wrong (measured 2026-11-23, about 8:50 PM PST): telemetryd read one TPS folder, ArchBig's, by one fixed path.
ArchSmall, Steve1 and Steve2 each write the same record in their own folder, and no source read them. No series, event or
row carried a game, so a second game's rows could not have been told from ArchBig's, and the alarm state was one dict.

The shape: the games come from `game_names.GAMES`. A game on the store's own machine is read from its folder. A game on
another machine is copied, append-only, by `pull_games.py` (one ssh call a minute per machine, `rm-telemetry-pull.timer`)
into `<root>/inbox/games/<machine>/`, and read from there. Every point, event and bridge row carries its `game`.

## ACCEPTS (the only inputs this is built for)

- **a-game-name.** What `game_names.key` takes: ArchBig, ArchSmall, Steve1, Steve2 in any letter case, and the old keys.
- **a-games-record.** `JawaBench/tps/tps_*.jsonl` (with `flight/` and `exc/`), append-only, one segment per name; and one
  `bridge_calls.jsonl` per machine, rotated by rename to `.1`, each call naming its endpoint's port.
- **a-machine-reached-by-ssh.** `host_guard.SSH_TARGETS` says how, `host_guard.RUNNER_DIR` says which clone there
  resolves that machine's own folders (`game_paths`, `game_instance`, `rmpaths`). No path of another machine is written
  here.

## DOES NOT SURVIVE (not promised)

- **a-record-deleted-before-it-was-pulled.** The game keeps 7 days of segments; a machine unreachable for longer loses
  what its game deleted meanwhile.
- **arming-the-test-tier-of-another-machines-game.** `telemetry tier --game Steve1` is refused: the bridge is driven on
  the game's own machine.
- **bridge-rows-before-2026-11-23.** They carry no game. `telemetry bridge --game X` counts them apart, as unlabelled.
- **game-series-before-2026-11-23.** They carry no `game` label and are ArchBig's: ArchBig was the only game read.
- **an-old-flattened-exception-copy-whose-source-is-gone.** Its first-sight rows keep their legacy attribution.

## PROMISES (each one is owed a test of the same name)

- **a-game-name-reads-that-games-rows-and-no-others.** With rows of all four games in the store, each verb that takes
  `--game` answers with the rows of that game only, in any letter case, and an old key reaches the same rows.
  First-sight exception text follows its source game, including signatures outside the sample's top five. `tier --game`
  uses the named local game's bridge and refuses conflicting inherited settings before connecting.
- **an-unknown-game-is-refused-by-name.** Exit 2, the name typed and the four names known in the refusal; no default game.
- **an-unreachable-machine-reads-could-not-look-with-its-cause.** Exit 3 and the cause when the machine, the pull, or the
  daemon could not be read; never a count of zero and never an empty list. Rows held from before are shown with their age,
  still with exit 3. Empty `events` results and empty event or bridge sections of `at` read UNMEASURED even when TPS rows
  are held.
- **a-game-with-no-data-yet-reads-no-data-yet.** Reached, and it has written no row: exit 4, never "could not look" and
  never zero.
- **a-game-that-is-down-reads-down-with-the-age-of-its-last-row.** The machine was read, and the process that wrote the
  newest row is gone: "down", with the age. An unread process list, including a refused local Windows snapshot, reads
  "process unread". A successful empty process list reads "down" when the newest row names a writer.
- **every-answer-carries-its-age.** The answer names the age of the game's newest row and of the last look at it; a row
  older than the fresh line of a game that is up reads STALE. The age is corrected for the other machine's clock.
  A failed game check keeps that game's last successful look, even if a game on the same machine was just read.
- **one-games-alarm-state-never-mixes-with-anothers.** The alarms read the store's own first game. A stall or a low
  speed of another game is kept as that game's event, raises no alarm, and leaves the first game's alarm state
  unchanged; a second game that is up does not read as "the record of the first is silent". Low speed uses the same
  normal-speed threshold and records one event per episode, including across a daemon restart.
- **a-session-without-windows-folders-on-path-finds-python.** The command works in an ssh session on the store's
  machine; with no Windows python at all it reads "could not look", exit 3.
- **a-backlog-being-read-is-a-live-daemon.** The heartbeat is written between files, so a daemon that drains a long
  backlog is not read as a dead one.
- **a-pull-copies-each-byte-once.** A pull appends what is new; a rename-rotated file is renamed, not copied again; a cut
  transfer is resumed at the next pull; a replaced file is copied whole. A rotation between listing and opening a file
  cuts that transfer before it sends any bytes from the replacement. The next pull copies both logs byte for byte.
- **the-tps-report-takes-a-game-name-too.** `tps_record.py --game Steve1` reads that game's record, and answers an
  unknown name, an unreachable machine and a game with no record as the CLI does (exit 2, 3, 4).
- **no-machine-path-or-game-is-hard-wired.** The telemetry code names no game and no path of another machine: a fifth game
  added to the map gets a source, a reading and a refusal text with no other edit.
- **a-machine-without-the-store-asks-the-one-that-has-it.** The `telemetry` command on another machine runs on the
  store's machine over ssh; when that cannot be reached it reads "could not look", exit 3.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
