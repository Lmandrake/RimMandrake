# BOUNDARY: the tick takes the game-only exit itself, after the version's offline Problems (maturation_autonomy.py _road_back, version_bugs, gameonly_and_land, execute; maturation_dispatch.py pilot_holders), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_autonomy.py` (`_road_back`, `version_bugs`, `read_version_bugs`,
`gameonly_key`, `gameonly_and_land`, the `autogameonly` act in `resolve` and `execute`, `fixer_brief` for
`fix_for="version"`) and `src/RimMandrake/rimflow/maturation_dispatch.py` (`pilot_holders`, `road_back_holder` with a `game`, `NO_SLOT_AUT`). **This page
covers only what the tick does at an offline stage when every open road-back item needs a game.** Item
`RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS`. Measured 2026-11-20: FlowWorks sat at Stage 3
(offline_build) for 515 minutes with 10 open road-back items, all `game-up` or `bridge`. The tick read `game_only` and only
printed `maturation.py advance FlowWorks --to in_game --game-only ...` for a hand, though a read-only evaluate of that
move passed every clause. The blind-exit reader (`design/specs/2026-11-19-maturation-game-only-blind-exit/boundary.md`)
is a separate page. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_tick_game_only_exit.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-game-only-road-back.** An open `s["road_back"]` whose items (`M.ledger_items_caused_by`: `{id, needs}`) all have
  `needs` in `M.LIVE_NEEDS`, on a row whose stage is in `M.OFFLINE_STAGES`.
- **a-version-problem.** A ledger item of kind `bug` whose title starts `<mod id> <version>` followed by a character that
  is not a word character or a dot (`FlowWorks 0.1.0, Convergent (a Problem): ...`), in no live-game window.
- **an-act-booking.** `st["mods"][mod]["steward"][<ver>|<stage>|game_only|<sha12 of the sorted ids>]`, as `execute`
  books it: `at`, `failed`, `tries`, `items`, `landed`.

## DOES NOT SURVIVE (not handled)

- **a-problem-titled-by-display-name.** A version Problem titled by the mod's display name (`Gimme Some Slack 0.1.1: ...`)
  and not by its id is not read as the version's, so the exit does not wait on it.
- **a-problem-of-another-kind.** A version Problem filed as kind `task` or `owed` is not read; the review files Problems
  as kind `bug`.
- **a-move-that-writes-outside-the-mod.** A move whose writes land outside `design/concepts/<mod>/` (its top-level files,
  `version/` top level and `ledger/`) is landed and put back only for the files inside those folders.

## PROMISES (each one is owed a test of the same name)

- **game-only-road-back-takes-the-exit.** With no open version Problem, the row is the act `autogameonly` (`aut` and
  `decision`), with `game_only_items` the open ids, a steward key `<ver>|<stage>|game_only|...`, no `fix_item` and no
  Needs Conductor line. The act is in `ACTS` and in `NO_SLOT_AUT`, so it takes no run slot.
- **version-bug-goes-before-the-exit.** With an open version Problem, the row is a `fixer` on it with `fix_for` set to
  `version`, and no exit is taken. Its brief is the version-Problem brief: it is never told to drop the item, and it never
  takes the bridge.
- **spent-version-bug-holds-the-exit.** When every open version Problem has had its one fixer run, the row reads
  `fixer_spent` with no `aut`. Its Needs Conductor line names the Problems and the hand move (`--game-only`).
- **unreadable-version-bugs-take-no-exit.** When the version Problems cannot be read, the row reads `blind` and takes no
  act.
- **version-bugs-read-by-title-kind-and-needs.** `version_bugs` returns only open items of kind `bug` in no live window
  whose title starts `<mod> <ver>`, not `<mod> <ver>1` and not another mod's. They are ordered by `created_index`. With
  no version, it returns None.
- **act-advances-and-lands.** `gameonly_and_land` moves the record to `in_game` by `DISPATCH`, with `game_only` confirmed
  on the named ids. It lands, in one landing, the stage record, `journal.md` and the other files the move wrote, all
  under `design/concepts/<mod>/`.
- **unlanded-act-puts-files-back.** When the landing fails, every file the move changed is put back byte for byte, every
  new file is removed, and the act raises.
- **refused-act-raises-and-writes-nothing.** A move that `maturation.advance` refuses (here an open sibling item left
  unnamed: the `game_only` clause) raises with the refused clause. It writes no file and lands nothing.
- **execute-books-the-act-once.** `execute` runs the act once and books it under its steward key, with the items and the
  landing's line. The row reads `launched`.
- **pilot-holder-waits-for-the-version-problem-fixer.** At an offline stage, a pilot mod whose open road-back items all
  need a game, and whose version Problem still has its fixer run owed, gets no holder launch: its version-Problem
  `fixer` row stays as the autonomy layer wrote it. The fixer may change the build that the game-only items test.
- **a-spent-game-only-set-goes-to-a-free-game.** At an offline stage, a pilot mod whose open road-back items all need a
  game, and whose version Problems are spent (`fixer_spent`), gets one live holder run on those items, on the first
  free game by `pick_game` (`design/specs/2026-11-20-per-game-hold-own-install/boundary.md`). A game that a live
  in-game run drives, or that a launch of this tick took, is not free. The row reads `launch`, names the game in its
  why and in `holder_game`, and keeps no PAUSED Needs Conductor line. Why: when the version Problems are spent, no act
  of the pipeline changes the build, so the game-only items no longer wait for a changing build; they waited only for
  a hand. Measured 2026-11-20 8:19 PM PST: FlowWorks held 10 game-only items behind one spent Problem (an owner look at
  water colour), game a drove the Pyrelands visit, and game b was free, and nothing sent work to game b.
- **no-free-game-names-each-game.** When no game is free for that run, the row reads `no_game_free`, a wait (`WAIT`)
  that ends by itself when a game frees, with no Needs Conductor line. Its why and its `waits_on` name each game and
  the reason it cannot take the run. They never say "the live game".
- **the-offline-holder-run-drives-its-named-game.** `road_back_holder` with a `game` at an offline stage starts the run
  on that game: the live brief, the game's own section (`game_instance.brief`) and `RM_GAME_INSTANCE` for that game. It
  does not refuse the game-only items.

Later lists beside this page: `polish.md` (two lines); `next_version.md` (none yet).
