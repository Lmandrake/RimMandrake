# RIMMANDRAKE_SCOPE_SELFTEST_LEDGER_READS_PREFLIGHT_LOG_TRIPS

## spec

`selftest_reconcile.py` (`ledger_bytes`) and `selftest_built.py` (`ledger_events`) read every `*.jsonl` under their
throwaway case directory as ledger events. Since the ticket preflight began logging each run to
`<state>/refusals/preflight_runs.jsonl` (2026-11-18), that file lands in the case directory too; its rows carry no
`event` key, so five cases die with `KeyError: 'event'` (selftest_reconcile 15/17, selftest_built 21/24 on
origin/main fe7c4ea9eb, measured 2026-11-18 by RIMMANDRAKE_WORK_VALID_OLD_ERA_TICKETS_NO_STALE_CRUD).
The test, not rimflow, is wrong: read only the files the ledger is made of, `model.ledger_files(<case>/events.jsonl)`.

## verify

Acceptance test (watched failing on fe7c4ea9eb: 15/17 and 21/24):

    python3 src/RimMandrake/rimflow/selftest_reconcile.py && python3 src/RimMandrake/rimflow/selftest_built.py

passes 17/17 and 24/24.

## criteria

- L0: both selftests pass in full on the landing commit.
