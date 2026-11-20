# BOUNDARY: `code_review_status.py check`, what CLEAN means, and FLAGGED, Design Version 0.2.0

Code: `src/RimMandrake/Utils/code_review_status.py` (`page_states`, `code_files`, `cmd_check`, `flags`, `cmd_flag`,
`cmd_unflag`, `cmd_list`, `cmd_mark_clean`). Item:
`RIMMANDRAKE_ENACT_CLEAN_MEANS_PROMISES_TESTED_ONE_FIX_ROUND`, written 2026-11-19. The owner's ruling of 2026-11-19
(`design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested): for all code, CLEAN is judged
against a stated page of promises with named covering tests; the reviewer fixes a significant finding, and one blind
reread checks the fix. `check` reads the pages
(`design/specs/*/boundary.md`) and the tests files that `src/RimMandrake/Utils/boundary_check.py` `PAGES` registers;
the promise-to-test match is `boundary_check.promises`, `tests_in` and `test_name`. Each promise has a test of its name
in `src/RimMandrake/Utils/selftest_code_review_page_state.py`, each watched failing on the base `84a50ad44c`.

Version 0.2.0 (item `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG`, 2026-11-19) adds FLAGGED, from the
owner's card of 2026-11-19 5:54 PM PST: when the one blind reread of a fix also finds and fixes a significant finding,
the file is flagged and nobody reviews it again; flagged files are examined about weekly. The FLAGGED tests were
watched failing on the base `b57a0b2520` (14 failures), except `t_a_flag_changes_no_page_state`, which guards against
a change and passed there; six planted faults in the new code each turned the tests red.

## ACCEPTS (the only inputs this is built for)

- **repo-paths.** One or more file paths inside the repo root, absolute or repo-relative.
- **a-code-line.** A page names its files in its first `Code:` or `Source:` sentence (up to the first `.` outside
  backticks that a space or the line end follows), each file in backticks: a full repo path; a path relative to an
  ancestor folder of a full path in that sentence (`rimflow/cli.py`); or a bare name in the folder of a full path in
  that sentence (`maturation_hands.py`). A backtick token that resolves to no file is not a file and is skipped.

- **a-flag-request.** `flag <path> --why "…"` or `unflag <path> --why "…"` with a path inside the repo root and a
  non-empty why. `list --flagged`.

## DOES NOT SURVIVE (not promised)

- **a-file-named-only-lower-on-the-page.** A file the page names after its `Code:` sentence (for example "the readers
  named below") is not read as named, and reads NO PAGE unless another page names it.
- **a-test-that-passes-without-checking-its-promise.** A tests file that exits 0 while a test body checks nothing
  makes the file read CLEAN. The fresh reader of the page and the review catch that, not `check`.
- **a-tests-file-red-for-its-environment.** A tests file that exits non-zero because its machine lacks something
  reads DIRTY with its exit code, not UNREADABLE; the exit code and the last output line are in the detail.

## PROMISES (each one is owed a test of the same name)

- **clean-needs-a-page-and-passing-tests.** A file reads CLEAN (exit 0) only when at least one registered page names
  it, every promise on each naming page has a test that the tests file's `main()` runs, and each naming page's tests
  file exits 0. The detail names the page and `promises covered N of N`.
- **a-promise-without-a-test-is-dirty.** When a promise on a naming page has no test, or `main()` never runs it, the
  file reads DIRTY (exit 1) and the detail names the promise and the test name it is owed.
- **a-red-tests-file-is-dirty.** When a naming page's tests file exits non-zero, the file reads DIRTY (exit 1) and the
  detail names the tests file and its exit code.
- **no-page-is-its-own-answer.** A file that no page names reads `NO PAGE` (exit 4), never DIRTY and never CLEAN.
- **could-not-look-is-its-own-answer.** When a page that names the file is not registered in `PAGES`, its page or
  tests file cannot be read or parsed, its tests file cannot be started or does not end within `TESTS_TIMEOUT_S`, or a page has no readable `Code:` or
  `Source:` sentence (so whether it names the file is unknown), the file reads `UNREADABLE` (exit 3) with the cause,
  never CLEAN or NO PAGE. It reads DIRTY only when another page that names it reads DIRTY; the detail then names both.
- **a-review-record-cleans-nothing.** A `mark-clean` record whose hash matches the bytes on disk does not make
  `check` read CLEAN; without a page the file reads NO PAGE.
- **the-worst-answer-sets-the-exit.** Over several paths the exit is 1 when any reads DIRTY, else 3 when any reads
  UNREADABLE or UNREVIEWABLE, else 4 when any reads NO PAGE, else 0.
- **each-tests-file-runs-once.** One `check` call starts each tests file at most once, however many of its paths a
  page names.
- **record-mode-keeps-the-review-record.** `check --record` answers from the review record as `check` did before
  this page (CLEAN when the recorded hash matches the bytes, else DIRTY; exit 0 or 1), for callers that track a
  review round and not cleanliness.

- **flag-records-why-and-sticks.** `flag` appends one record (path, why, seat, time, the file's hash) to
  `infrastructure/state/code_review/flags/<SEAT>.jsonl`, and the path stays FLAGGED however its bytes change, until
  `unflag`. A flag with no `--why`, or of a path that is not a file, is refused (exit 2) and writes nothing.
- **list-flagged-names-each-flag.** `list --flagged` prints one `FLAGGED  <path>  <time> <seat>: <why>` line per
  flagged path and exits 0; with none it says that no file is flagged. When a flag shard cannot be read or parsed it
  prints `UNREADABLE` with the cause, no FLAGGED line, and exits 3.
- **a-flagged-file-is-not-picked-for-review.** `list` (with or without `--show-untracked`) counts a flagged path as
  FLAGGED in its own tally, never as DIRTY or NEVER ENTERED. `mark-clean` of a flagged path is refused (exit 2),
  writes no record, and names `unflag`.
- **unflag-ends-the-flag.** `unflag` appends an unflag record, and the path is then not in `list --flagged`. An unflag
  of a path that is not flagged, or with no `--why`, is refused (exit 2).
- **a-flag-changes-no-page-state.** `check` and `check --record` answer the same states and exit for a flagged path
  as for the same path unflagged. A flag is not a page state.

## LIMITS

- **tests-timeout.** `TESTS_TIMEOUT_S` = 600 s per tests file run. Danger: a tests file that never ends hangs `check`
  and each caller (`ship_check.py`, `run_mutation.py`, a publish). Evidence: open-ended calls hung runs before, and
  `call_deadline_lint.py` (`CALL_DEADLINES_ENFORCE_130_OPEN_ENDED`) refuses a subprocess call with no deadline. Past
  the limit the file reads UNREADABLE, never DIRTY.

Later lists beside this page: `polish.md` (none yet).
