# BOUNDARY: maturation.py's stage record (spend, version rollover, the offline build's facts), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py`. **This page covers only the parts of the stage record that
`RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE` (a Codex full-file review, 2026-11-18) found flaws in**:
`add_spend`, `spend_by_stage`, `next_version` and `build_facts`. Its reads of the outside world are the page beside
this one, `design/specs/2026-11-19-maturation-reads/boundary.md`; the record's other moves and gates (`advance`,
`evaluate`'s clauses) have no page yet. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_maturation_record.py`, each watched failing on the base `7df09c59a2`.

## ACCEPTS (the only inputs these parts are built for)

- **one-record-per-mod.** `design/concepts/<Mod>/version/stage_record.json`, written whole by `write_text` (a temp
  file, then `os.replace`), by processes on one machine that all take `_mod_lock` (an `flock` on
  `.stage_move.lock` in the mod's folder) before writing it.
- **spend-rows-may-lack-a-field.** A spend row (the record's `spend` list, or a RUN_SPEND line) may carry `tokens`,
  `usd` or `wall_s` as the string UNMEASURED: a run that could not read its own meter is ordinary. Every committed row
  carries a `token_unit` (the rows written before 2026-11-19 were stamped from their run records on 2026-11-22,
  `design/specs/2026-11-22-run-spend-and-model-alias/equivalence.md`).
- **numbered-evidence-belongs-to-one-version.** `version/blind_challenge/cycle_<N>/`, `version/in_game/visit_<N>/`
  and `version/walk_brief/arrival_<N>.md` are numbered by the record's counters (`cycles.total`, the in-game moves,
  `pre_human_arrivals`), which `next_version` starts again at 0.

## DOES NOT SURVIVE (not handled)

- **a-run-spend-file-unreadable-but-present.** A RUN_SPEND that exists and cannot be read reads as no rows, and
  `record_run_spend` then rewrites it with only its new rows. Listed, not fixed, on the reads page by the owner's card
  of 2026-11-19 (`a-mod-file-unreadable-but-present`): a file of ours turning unreadable on its own disk is rare.
- **a-writer-that-skips-the-lock.** A process that writes the record without `_mod_lock` (a hand edit, an old copy
  of this module) can still erase a move in between.
- **an-archive-move-that-fails-half-way.** `next_version` sets each numbered folder aside with one `os.rename`; if a
  later rename or the record write fails, the ones already moved are moved back. A move back that fails too raises
  naming the paths left in the archive.

## PROMISES (each one is owed a test of the same name)

- **spend-write-holds-the-mod-lock.** `add_spend` reads, changes and writes the record while holding `_mod_lock`: an
  `advance` cannot land between its read and its write and be erased.
- **stage-spend-unmeasured-when-no-row-measured.** `spend_by_stage` gives `tokens`, `usd` and `wall_s` as UNMEASURED
  for a stage where no row measured that field, never 0; a stage where some rows measured it sums those rows. `show`
  prints such a field as UNMEASURED.
- **build-facts-refuses-what-evaluate-refuses.** `build_facts`'s `refused_bars` holds every bar `evaluate`'s
  `every_bar_has_a_check_that_runs` clause counts as owed scene parts (a deciding scene whose `owed_parts_item` is
  still open on the ledger), kept through the walk and live-red exemptions as `evaluate` keeps it: the builder is
  never launched with `refused_bars=[]` while the exit refuses on such a bar, and its brief names the open item.
- **next-version-sets-aside-numbered-evidence.** `next_version` moves the previous version's numbered evidence (the
  three kinds above) to `version/previous/<old version>/` under the same relative path, before the new record is
  written, and names every moved path in its result (`archived`, `aside`), its journal entry and its CLI line; an
  archive path already taken refuses the move before anything moves. The new version's cycle 1, visit 1 and arrival 1
  start empty, and the old version's evidence is kept (`modledger.py` still reads its fault ids).
- **next-version-refuses-a-move-made-meanwhile.** `next_version` writes its new record only if the record on disk
  still has the stage, version and number of moves that it read (`commit_move`'s `expect`). When a move landed in
  between, it returns `ok` False, keeps that move and moves the set-aside evidence back.
- **seed-writes-under-the-mod-lock.** `seed_mod` reads again under `_mod_lock` before it writes. A record that another
  process wrote while this one gathered its facts is returned untouched (`made` False), never written over.

- **spend-rows-carry-their-unit.** Every spend row a writer adds names its `token_unit`. A run row (`_spend_row`, so
  the seed and `record_run_spend`) takes its run record's unit, which the maturation_now run view carries
  (`role_launch.stored_unit`: the stamp, else weighted_v1). `add_spend` stamps weighted_v2. The seed's VERSION.json
  row takes the unit that VERSION.json names, else `unstated`. A run row names its run's model.
- **stage-spend-sums-one-unit.** `spend_by_stage`, `pass_cost` and `show` add weighted_v2 rows only into `tokens`
  (`weighted_tokens`). Every other unit is summed apart, by unit, in `tokens_other`. It is never converted or mixed
  in, and `show` prints each unit under its own name. A row's unit is `row_unit`, which is
  `role_launch.stored_unit` (design/specs/2026-11-22-run-spend-and-model-alias/boundary.md). Items
  RIMMANDRAKE_STAMP_STAGE_SPEND_ROWS_ONE_UNIT and RIMMANDRAKE_RELABEL_SPEND_PRINTERS_STILL_V1; both tests were watched
  failing on 9c3ad408cd.

Later lists beside this page: `polish.md`; `next_version.md` (none yet).
