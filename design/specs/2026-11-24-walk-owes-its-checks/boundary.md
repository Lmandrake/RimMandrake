# BOUNDARY: a mod does not stand at his walk with in-game checks owed (maturation.py walk_owed, unrun_owed; maturation_autonomy.py the act `autovisit`), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`unrun_owed`, `walk_owed`, `landed_at_walk`, the clauses `unrun_run` and
`walk_checks_stand` and the Stage 7 road of `evaluate`, `unrun_lines`, `ingame_to_run`) and
`src/RimMandrake/rimflow/maturation_autonomy.py` (`_walk_owed`, `visit_and_land`, the act `autovisit` in `resolve` and
`execute`). Tests of the same names: `src/RimMandrake/rimflow/selftest_walk_owes_checks.py`.

The failure (2026-11-24, item `RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED`): commit a6f05380df
changed Pyrelands' C# at Stage 7. Ten checks were recorded UNRUN. Only the Stage 6 brief read that file, and nothing read
the build match after Stage 6, so the mod moved to his walk at 4:50 AM PST with all ten not run.

The question: at Stage 7 or 8, must a check run in a game before he walks?

## ACCEPTS (the only inputs these parts are built for)

- **an-unrun-row.** A row of `version/in_game/unrun.jsonl` as `maturation.py unrun` writes it: `check`, `sha` (a commit),
  `command`, `at`.
- **a-visit-record.** The rows of the visits on disk, and the Stage 6 build match of the last visit
  (`read_ingame_exit(...)["build_match"]`), whose rows carry the change relation's state for each check.
- **a-stage-seven-or-eight-record.** A stage record at `pre_human` or `his_walk`.

## DOES NOT SURVIVE (not handled)

- **a-walk-that-another-cause-spoils.** The Stage 6 exit reads game-build differences and list differences outside
  the published small list. The tick and next visit plan use a change to that list to
  find the rows whose mod-list relation is touched or unreadable
  (`design/specs/2026-11-21-rerun-only-related/boundary.md`, `mod-list-only-reruns-related-rows`).
- **a-walk-he-makes-with-no-hold.** The act reads his OWNER hold and the stops on ArchBig. It cannot see a walk that he
  makes with neither.
- **a-reader-that-made-the-commit.** A commit names no unit, so that its reader is another run is the reader's word.
- **a-check-added-after-stage-six.** A check that joined the table after the Stage 6 exit has no row and is not owed here.

## PROMISES (each one is owed a test of the same name)

- **an-unrun-row-is-owed-until-a-row-on-its-commit-or-later.** An UNRUN row is met when the deciding row of its check ran on a
  commit that contains the UNRUN row's commit; a spoiled run meets nothing. When git cannot resolve a commit, the row is
  met only by a row of a visit that opened after the UNRUN row was written. A check with no row is owed.
- **a-check-that-left-the-table-is-not-owed.** A check that another check replaces, that moved to the next version, or
  whose raid scene is paused is not owed.
- **a-check-outside-the-table-holds-no-move.** An UNRUN row whose `check` is no stage-6 in-game check of the table stays in
  the visit brief and holds no move: no program can know its row. (ExplosiveKnockback has two, written as prose.)
- **the-visit-brief-lists-only-owed-unrun-rows.** The Stage 6 brief lists the UNRUN rows still owed, and not the met ones.
- **an-owed-unrun-check-runs-in-the-next-visit.** `ingame_to_run` names a check whose UNRUN row is owed, whatever its
  earlier PASS.
- **stage-six-exit-waits-for-the-unrun-rows.** The move `in_game` to `pre_human` is refused (`unrun_run`), by check, while
  an UNRUN row is owed.
- **no-walk-while-a-check-is-owed.** The move `pre_human` to `his_walk` is refused (`walk_checks_stand`), by check, while an
  UNRUN row is owed or a check's row stopped counting because a change touches it or its relation cannot be read.
- **could-not-look-is-not-clean.** When a change touches a check and the build match cannot be read (no Exit block, an
  unreadable walk build), that move is refused with the cause, and the tick takes no act.
- **untouched-checks-read-no-walk-folder.** When the change since the rows touches no check, the walk build is not read
  (measured 2026-11-24: 32 s of the 44 s a reading of Pyrelands took).
- **stage-seven-goes-back-only-for-an-owed-check.** The move `pre_human` to `in_game` passes `order` only while a check is
  owed; Stage 7 has no other road back.
- **a-fix-that-landed-at-the-walk-owes-a-reader.** When a visit opened from Stage 7 or 8 with no walk result, each commit
  that changed the mod's shipped C# or XML between the Stage 6 exit and that opening owes one fresh reader: the visit's
  exit is not met, and names it in `fix_readers_owed`, until the `fix_reviews.jsonl` of that visit or an earlier one
  holds a `sound` row with that commit in `fix`. A commit list that git cannot give keeps the exit not met, by cause. (a6f05380df: nothing saw its
  owed reader.)
- **the-tick-opens-the-visit.** At Stage 7 or 8 with a check owed, the tick's row is the act `autovisit`: the record moves
  to `in_game` by `DISPATCH`, landed, and the next visit opens, which runs on a free game. The act takes no run slot.
- **his-hold-keeps-the-walk.** At Stage 8, while ArchBig is under his hold or a stop, or who holds it cannot be read, the
  row stays the owner's, names the owed checks, and takes no act.
- **nothing-owed-changes-nothing.** With no check owed, Stage 7 gets its walk brief and Stage 8 is his, as before.
- **an-unlanded-visit-move-puts-files-back.** When the landing fails, every file the move wrote is put back and the act
  raises.
- **a-visit-planned-on-a-stage-the-record-left-moves-nothing.** When the record left the stage that the tick planned the
  act on (another run moved it between the plan and the act), the act moves and lands nothing, and the row reads
  `settling`: no `launch_failed`, no failed booking and no form repair. The next tick plans from the new stage.
  (FlowWorks, 2026-11-25 8:18 PM PST: the walk-findings route moved it to `offline_build` 2 minutes before the act, and
  the `order` refusal filed RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_SEVEN.)

Later lists beside this page: `polish.md`.
