# BOUNDARY: the blind exit on a game-only move (maturation.py read_exit, exit_met_clause, evaluate), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py`. **This page covers only how the blind exit reads a game-only move**:
`read_exit` and `_lane1_deferred` with `game_only_bars`, `exit_met_clause` passing it on, `evaluate` giving it only
when the move's `game_only` clause passes, and `bars_named_by`. Item `RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT`;
the Conductor's mindful act on it picked this reader change (route b) over his OWNER event (route a). Each promise has a
test of its name in `src/RimMandrake/rimflow/selftest_maturation_game_only_exit.py`, and a planted fault that turns that
test red in `src/RimMandrake/rimflow/acceptance/game_only_exit_guards_break_accept.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-game-only-move.** `evaluate(..., to="in_game", game_only=[ids])` on a record at an offline stage, where the
  `game_only` clause checks the items (open, needs game-up or bridge, every open sibling named, the record came from
  Stage 6). Only then does the blind exit read the game-only way.
- **a-bar-named-in-a-title.** A game-only item carries a bar when its newest ledger title names the bar's id as a
  whole word (`FlowWorks 0.1.0 inv_drilling in game: ...`). The item's prose is not read.
- **a-cycle-in-the-format-notes-layout.** The cycle's files are those `read_exit` reads for every blind exit.

## DOES NOT SURVIVE (not handled)

- **a-judge-false-for-a-reason-no-file-check-reads.** In a cycle that FIXED a Problem and passes every file check, the
  judge's `exit_met: false` is read as the owed new blind judge, whatever the judge's prose gives as the reason.
- **a-title-that-names-a-bar-in-passing.** An item whose title names a bar it does not prove ("unlike inv_x, ...")
  still carries that bar.

## PROMISES (each one is owed a test of the same name)

- **game-only-exit-skips-owed-judge-and-named-rows.** With `game_only_bars`, a cycle whose only gaps are the new blind
  judge owed for its own FIXED Problems (each shown red then green) and lane-1 `not_kernel` UNSETTLED rows whose every
  bar a named game-only item carries reads `met`, and the reading names both.
- **unfixed-problem-still-refuses.** With `game_only_bars`, a Problem whose status is not FIXED still reads `not_met`.
- **offline-row-without-named-item-still-refuses.** With `game_only_bars`, a lane-1 row with one offline bar that no
  named item carries still reads `not_met`, also when its other bars are carried.
- **not-game-only-move-unchanged.** Without `game_only_bars`, `read_exit` gives the same reading as before this change:
  the owed judge and the lane-1 rows on offline bars read `not_met`, and `exit_met_clause` refuses.
- **owed-judge-from-other-cause-still-refuses.** With `game_only_bars`, a judge's `exit_met: false` in a cycle that
  fixed nothing, a FIXED Problem not shown red then green, or a red offline bar still reads `not_met`.
- **evaluate-gives-bars-only-when-game-only-passes.** `evaluate` hands `exit_met_clause` the bars only when the
  `game_only` clause passes: a move with no `--game-only`, or one whose items fail that clause, gets None.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
