# BOUNDARY: maturation.py's reads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py`. **This page covers only its reads of the outside world**: the 29 places
the could-not-look lint (`src/RimMandrake/Utils/could_not_look_lint.py`) finds there, each read and classed on
2026-11-19 by `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS` (parent
`RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED`). The stage record's moves and gates have no page yet. Each
promise has a test of its name in `src/RimMandrake/rimflow/selftest_maturation_reads.py`, and a planted fault that
turns that test red in `src/RimMandrake/rimflow/acceptance/lint_reads_promise_breaks_accept.py`. Each place's class and
reason is in the lint's allowlist, `src/RimMandrake/Utils/could_not_look_allowlist.json`, under `reasons`.

Owner, by card 2026-11-19 (the item's "What the card said"): a rare failure that breaks a promise is listed below as
not handled, and no fix is built.

## ACCEPTS (the only inputs the reads are built for)

- **mod-files-written-whole.** The stage record and the other files this module rewrites go through `write_text` (a
  temp file, then `os.replace`); the JSON-lines files (unrun.jsonl) are appended a whole line at a time.
- **files-a-stage-may-lack.** A journal, a steward file, a run-spend file, an unrun file, a lane file that is absent
  means nothing was written there yet, and reads as empty.

## DOES NOT SURVIVE (not handled)

- **a-mod-record-that-does-not-parse.** `load` drops `read_json`'s reason, so a record.json that does not parse reads
  as no record (`load(...) or {}`): `evaluate` refuses with the stage UNMEASURED, `commit_move` raises MovedMeanwhile,
  `brief_text` writes an offline-build brief whatever the stage, and the blind and in-game briefs lose the record's
  fields.
- **a-mod-file-unreadable-but-present.** `read_text` and `_jsonl` return None on any OSError, the same as absent: an
  unreadable journal.md reads as no Conductor hold in `evaluate`'s hold clause, a steward file as the standing default,
  RUN_SPEND as no spend (and `record_run_spend` then rewrites it with only the new rows), a blind cycle's SUMMARY.md
  and lane files as no debts (`ingame_debts`), a visit's rows.jsonl as no evidence writer (`evidence_writers`), lane2's
  reruns after fix and fixes as none (`read_exit`), unrun.jsonl as no UNRUN row (`read_unrun`).
- **unparseable-json-at-the-lock-commit.** `_git_show` reads JSON that does not parse at a commit as None, the same as
  a path the commit lacks.

## PROMISES (each one is owed a test of the same name)

- **absent-only-when-measured.** `_absent(path)` is True only when the stat says the path does not exist; a stat that
  fails any other way is False.
- **mod-json-read-names-its-failure.** `read_json(root, mod, p)` returns `(None, "no file")` for an absent file,
  `(None, "unreadable JSON")` for one that does not parse, and `(value, None)` for one that does.
- **unread-ledger-endings-is-none.** `ledger_live_endings` returns None when the ledger's events folder or a shard in
  it cannot be read, and 0 endings for an item when a read shard holds none.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
