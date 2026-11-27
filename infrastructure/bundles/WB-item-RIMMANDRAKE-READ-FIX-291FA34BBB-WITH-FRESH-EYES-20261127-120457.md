# Work bundle WB-item-RIMMANDRAKE-READ-FIX-291FA34BBB-WITH-FRESH-EYES-20261127-120457: state

System: item:RIMMANDRAKE_READ_FIX_291FA34BBB_WITH_FRESH_EYES. One member, one group. State: done.

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_READ_FIX_291FA34BBB_WITH_FRESH_EYES | REAL (fresh read found one Problem) | fixed, file FLAGGED | add29c6fd0 (test), a425c8af59 (flag) |

- The read: `src/RimMandrake/rimflow/selftest_work_bundle.py` whole, against
  `design/specs/2026-11-24-work-bundles/boundary.md`. Selftest PASS before and after.
- The Problem (reason 2, the promise has no test that goes red): `a-code-bundle-gets-one-fresh-read`. Every case
  injected `commits` and `owed`, so `bundle_commits` (git fetch, log, parse) and `reader_step`'s own owed (the
  exclusion of files that an open reader ticket names) never ran. Seen: the parent test file reads PASS with
  `--name-only` removed from `bundle_commits`.
- The fix: one new case with a throwaway git origin and clone, where only the filer is faked. It is red on fault 1
  (`--name-only` removed) and on fault 2 (the open reader paths dropped from the own owed), and green on the build.
  A third planted fault (the `--since` filter removed) stays green, and that is correct: `plan_reader` filters by
  the bundle start time a second time.
- Polish: no line of `design/specs/2026-11-24-work-bundles/polish.md` names the file.
- The publish was killed once at the harness's 10-minute background limit (the publish door's queue was long). The
  local commit was then landed with `land.sh`.
