# RIMMANDRAKE_ACCEPT_REPAIR_RECORD_NAMING_TWO_COMMITS_NOT_ONE

Caused by RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_TWO_FAILURES_BACK (steward run, Pyrelands in-game visit 2, 2026-11-21).

## spec

`repair_shown` in `src/RimMandrake/rimflow/maturation.py` matched the whole `repair.commit` field against `SHA_RE`.
The Pyrelands visit-2 driver made one repair in two commits and wrote `"commit": "9b4ad4ab14 a7d25d9f33"`. So
`sc_firehawk` read `unhandled`, and `sc_firehawk_rewards` and `firehawk_first_sighting_letter` read `needless`, though
each row records its planted FAIL reading and its PASS on the real build. Fix: the field holds one or more commit
hashes, separated by spaces or commas. Each word must still be a commit hash.

## verify

`python3 src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py` (test `repair-in-two-commits-counts`).
Seen red on the parent (1 test red), green on the fix (17 tests, every planted fault caught).

## criteria

- A repair that names two commit hashes, by space or comma, counts as shown.
- A repair that names a hash and a word that is not a hash does not count.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py`, exit 0, 17 tests.
