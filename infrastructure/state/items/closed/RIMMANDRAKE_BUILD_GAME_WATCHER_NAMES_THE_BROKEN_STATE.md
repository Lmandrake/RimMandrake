# RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the watcher outside the game, on the heartbeat that the disk writer already gives: ticking, paused,
  frames stopped, an exception on every frame, stuck in a load, at the menu, no map, process gone. A run never starts
  on a game whose last state was broken. A broken game is stopped at once, on any game, and the stop is reported (root `CLAUDE.md` §Facts you cannot guess). It
  builds on `crash_watch.sh`, the stall dump and `game_health_check.py`. It comes before the run plan, which is the first ticket that changes a map by itself.
- **Needs:** nothing.

Depends on: nothing.

## verify

Acceptance test (offline), 10 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_game_watcher.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_game_watcher.py`, 10 checks: one per state (8); "never
  start on a broken game" (1); "could not read the heartbeat" is its own answer, never "ticking" (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 10 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a stale heartbeat file read as "paused"; an unreadable file read as "ticking".
- On any game, ArchBig included, the watcher stops a broken game and reports the stop.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
