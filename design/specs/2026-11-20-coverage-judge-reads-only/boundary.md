# BOUNDARY: the coverage judge's second reader reads and never edits (coverage_judge.py judge_tail), Design Version 0.2.0

Code: `src/RimMandrake/rimflow/coverage_judge.py`. **This page covers only the command line the coverage judge's second
reader is started with**: `judge_tail` with its default `may_fix=False`, and `READ_ONLY_DENY`. Item
`RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION` (point 6). The judge itself was read-only from that item
until the owner's ruling of 2026-11-25 ("A blind judge absolutely CAN fix and SHOULD fix!"): it now fixes a gap whose
repair lies in `scenes.json`, and a fresh judge checks the fix. That part, and its chain rule, are on
`design/specs/2026-11-25-blind-readers-fix/boundary.md`. The test of the promise here is in
`src/RimMandrake/rimflow/selftest_coverage_judge_reads_only.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-unit-and-a-schema.** The run's unit name, its label and the JSON schema of its answer.

## DOES NOT SURVIVE (not handled)

- **a-write-through-bash.** The denied tools are Edit, Write and NotebookEdit. A Bash command can still write a file.
  The second reader is shown only JSON and is told to read no file.

## PROMISES (each one is owed a test of the same name)

- **second-reader-cannot-edit.** The tail `judge_tail` gives by default (the second reader's) denies Edit, Write and
  NotebookEdit (`--disallowedTools`), keeps the model, the label, the JSON output and the schema, and passes no
  `--max-budget-usd`.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
