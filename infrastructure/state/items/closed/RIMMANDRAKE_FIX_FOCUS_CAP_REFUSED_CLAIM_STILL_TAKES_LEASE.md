# RIMMANDRAKE_FIX_FOCUS_CAP_REFUSED_CLAIM_STILL_TAKES_LEASE

Found 2026-11-18 by BENCH during `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` (sweep of tests).

## spec
`selftest_focus_cap.py` is red: case "direct claim: the refused claim wrote no event". A bare `rimflow claim` of a
fresh item at the focus cap is refused ("FOCUS CAP") and writes NO ledger event [measured 2026-11-18 by snapshotting
every file of the sandbox before and after the claim]. What it writes is one line in the ticket preflight's own run
log, `preflight_runs.jsonl`, which sits beside the sandbox ledger; the test's `model_read` walked every `*.jsonl`
there and counted that line as an event. (The "lease take" this item first named was the reservation `next` had
already written: the test sliced a concatenation of files by count.) Fix: the test reads only `model.ledger_files`,
as RIMMANDRAKE_SCOPE_SELFTEST_LEDGER_READS_PREFLIGHT_LOG_TRIPS did for selftest_built and selftest_reconcile.

## verify

Acceptance test (red at `99d4de3569`, watched: `FAILS: 1`):
`python3 src/RimMandrake/rimflow/selftest_focus_cap.py` exits 0.

## criteria

- A1 (offline): the acceptance test above exits 0.
