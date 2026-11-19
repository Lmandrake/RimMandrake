# RIMMANDRAKE_FIX_FOCUS_CAP_REFUSED_CLAIM_STILL_TAKES_LEASE

Found 2026-11-18 by BENCH during `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` (sweep of tests).

## spec

`selftest_focus_cap.py` is red: case "direct claim: the refused claim wrote no event". A bare `rimflow claim` of a
fresh item at the focus cap is refused ("FOCUS CAP"), but the throwaway ledger gains one event first:
`{"event": "lease", "action": "take", "id": "NAMEDA_FIX_NOT_STARTED"}`. So a refused claim still takes a lease. Not
caused by the era split as far as measured (`run_store.guard` returns None for an item not in the run store) [guess
~90%; not bisected].

## verify

Acceptance test (red at `99d4de3569`, watched: `FAILS: 1`):
`python3 src/RimMandrake/rimflow/selftest_focus_cap.py` exits 0.

## criteria

- A1 (offline): the acceptance test above exits 0.
