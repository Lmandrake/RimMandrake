# BOUNDARY: the reads of four files where a could-not-look bug was seen, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_autonomy.py`, `maturation_hands.py`, `coverage_judge.py`, `run_void.py`.
**This page covers only their reads of the outside world**: the places the could-not-look lint
(`src/RimMandrake/Utils/could_not_look_lint.py`) finds there, each read and classed on 2026-11-19 by
`RIMMANDRAKE_READ_ONLY_FILES_THAT_FAILED_PILOT_FOUND_ZERO` (parent `RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED`).
These four files were read because a could-not-look bug had been seen and fixed in each since the 2026-11-17 audit
(`RIMMANDRAKE_ABORT_AUTOLOCK_WHEN_BACKUP_UNREADABLE`, `RIMMANDRAKE_BOOK_FAILED_TICK_LAUNCHES_THREE_FALSE_HANDS`,
commits `b8d12099e5` and `5070199008`). The modules' decisions have their own pages. Each promise has a test of its
name in `src/RimMandrake/rimflow/selftest_failed_before_reads.py`, and a planted fault that turns that test red in
`src/RimMandrake/rimflow/acceptance/lint_reads_failed_before_breaks_accept.py`. Each place's class and reason is in
the lint's allowlist, `src/RimMandrake/Utils/could_not_look_allowlist.json`, under `reasons`.

Owner, by card 2026-11-19: a rare failure that breaks a promise is listed below as not handled, and no fix is built.

## ACCEPTS (the only inputs the reads are built for)

- **concept-files-written-whole.** A concept's `stage.json` is written by `designer_stage.write_json` (a temp file,
  then `os.replace`); a mod's `record.json` and `stage_record.json` by maturation.py's `write_text` (the same); the
  Dispatcher's `state.json` atomically. 0 of 325 JSON files under the clone's `design/concepts` fail to parse
  (2026-11-19).
- **times-in-iso-form.** Every history and release time in `stage.json` is ISO 8601 (700 of 700 parse, 2026-11-19), and
  every ledger event's `ts` is (60,387 of 60,387).

## DOES NOT SURVIVE (not handled)

- **an-unreadable-concept-stage.** `maturation_autonomy.designer_state` returns None for an absent and an unreadable
  `stage.json` alike. `_designer_lane` says `designer_unreadable` and holds the lane, but `final_stop` and
  `coverage_stopped` run first and see no stop, so a road-back launch is not held by a coverage stop on that concept.
- **an-unreadable-dispatcher-journal.** `designer_unit` reads an unreadable Dispatcher journal as no live Designer run:
  the wait row says the launcher runs it. It launches nothing.
- **an-unreadable-dispatcher-state-or-schedule.** `designer_chain` returns None both for "under the cap" and for "could
  not read": the row reads `designer_wait`, not `designer_chain_cap`. `role_launch.chain_ask` still refuses at the launch.
- **a-stage-time-that-does-not-parse.** `maturation_autonomy` (`coverage_stopped`, `chain_owed`, `final_stop`) and
  `run_void` (`_stop_before`, `_stage_restore`) read an unparseable time as 0, the oldest event: a stop, release,
  lock or locked change with such a time sorts first.
- **an-unreadable-maturation-record.** `resolve` falls back to `maturation.load`, None for absent and unreadable alike,
  when the facts carry no version: the row's version is None.
- **an-unreadable-stage-file-hides-hand-acts.** `maturation_hands._json` returns None for absent and unreadable alike:
  `collect` then shows no coverage release by hand (`stage.json`) and no move by hand (`stage_record.json`).
- **a-ledger-time-that-does-not-parse.** `collect` reads an unparseable ledger `ts` as 0, so a close from a window
  with that time is not shown as a hand act.
- **an-unreadable-concept-file-gives-no-entries.** `coverage_judge.entries` reads an unreadable or unparseable concept
  file as no entries of its kind, as it reads an absent one.
- **an-unreadable-concepts-folder.** `run_void.concept_dirs` reads a `design/concepts` it cannot list as no concepts,
  so `resolve` finds no staged runs.
- **an-unreadable-stage-file-hides-staged-runs.** `run_void._raw_stage` returns None for absent and unreadable alike:
  `children` and `resolve` then find no runs from that stage file (a recorded parent still finds them in the books).
- **a-verdict-time-that-does-not-parse.** `run_void._at` reads a verdict whose text or `at` does not parse as 0, so
  `swap_verdict(back=True)` puts the void judge's verdict over it.

## PROMISES (each one is owed a test of the same name)

- **unreadable-concept-stage-holds-the-designer-lane.** `maturation_autonomy._designer_lane` with no stage (None)
  records `decision: designer_unreadable` with a why naming `stage.json`, and nothing else.
- **unparseable-stage-time-is-no-time.** `maturation_autonomy._iso_ts` and `run_void.parse_time` return None for a time
  that does not parse (`UNMEASURED`) and the epoch for an ISO one; never 0.
- **blind-ledger-on-road-back-is-named.** `maturation_hands._road_back_items` with a ledger read that raises returns
  None (not an empty set) and keeps the cause in `h["road_back_error"]`.
- **unreadable-prior-verdict-is-no-baseline.** `coverage_judge.prior_verdict` on a verdict file that does not parse
  returns None without raising, so the next look is a full judge.
- **unreadable-run-record-spend-is-unmeasured.** `run_void.void_spend` with a run record that cannot be read (None)
  counts no dollars for it and lists its unit as UNMEASURED.
- **hand-run-the-books-now-own-is-folded.** `maturation_hands._fold_tick_own` folds, once, each open `hand_run` act
  whose unit the tick's current books (`tick_units`) hold, and leaves open every act whose unit no book holds.
- **lane-launched-run-is-no-hand-run.** A run whose unit the Workshop lane's books hold (`list_dispatch` `state.json`,
  live or cleared attempts: `maturation_hands.lane_units`) is recorded by `collect` as no hand run, and
  `_fold_tick_own` folds, once, an open `hand_run` act for such a unit, naming the lane. A run that no lane attempt and
  no tick book holds stays an open hand act; a lane state that cannot be read (`None`) folds nothing.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
