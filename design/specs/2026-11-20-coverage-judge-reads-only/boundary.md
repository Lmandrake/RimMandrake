# BOUNDARY: the coverage judge and its second reader read and never edit (coverage_judge.py judge_tail), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/coverage_judge.py`. **This page covers only the command line the coverage judge and its
second reader are started with**: `judge_tail` and `READ_ONLY_DENY`. Item
`RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION` (point 6, the contained half: "do not let it edit
files"). The judge ran with `--dangerously-skip-permissions` and every tool. The other half (the Designer session that
wrote the design is resumed to mend the judge's gaps, then the judge reads again fresh) is a design note on that item,
not built here. The test of the promise is in `src/RimMandrake/rimflow/selftest_coverage_judge_reads_only.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-unit-and-a-schema.** The run's unit name, its label and the JSON schema of its answer.

## DOES NOT SURVIVE (not handled)

- **a-write-through-bash.** The denied tools are Edit, Write and NotebookEdit. A Bash command can still write a file;
  the judge's input hashes (`fresh_key`, RIMMANDRAKE_HASH_EVERY_COVERAGE_INPUT) still refuse a signature on inputs
  that changed while it judged.

## PROMISES (each one is owed a test of the same name)

- **judge-cannot-edit.** The tail the judge and its second reader are started with denies Edit, Write and
  NotebookEdit (`--disallowedTools`), keeps the model, the label, the JSON output and the schema, and passes no
  `--max-budget-usd`.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
