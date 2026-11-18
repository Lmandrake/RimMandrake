# RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER

## spec
Codex review, 2026-11-18 (`D:\ClaudeWork\rimmandrake\evidence\pass_record\codex_round2.txt`, finding 3):
`src/RimMandrake/rimflow/maturation.py` `next_version()` starts the new record with `spend: []` but keeps
`version/run_spend.jsonl` (RUN_SPEND), whose rows name no version. `spend_rows()` appends every RUN_SPEND row, so
`maturation.py show` and `next` report an earlier version's Dispatch runs as this version's spend. `pass_cost()` (built in
e6bdc4d142) already keeps only run rows whose `at` is on or after the record's `seeded.at`; `show`/`next` do not.
Do NOT filter inside `spend_rows()` itself: `record_run_spend()` uses it to know which units are already recorded, and a
filtered list would re-add old units. Filter where spend is reported (or version the rows when written).

## criteria
- After a next-version, `spend_by_stage` as `show` prints it leaves out a RUN_SPEND row whose `at` is before `seeded.at`,
  and keeps one after; `record_run_spend` still writes no duplicate of an old unit.
- Acceptance test: a new case in `src/RimMandrake/rimflow/selftest_maturation.py` doing exactly the above (drafted here, not
  yet written or watched failing).

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation` GREEN with the new case.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
