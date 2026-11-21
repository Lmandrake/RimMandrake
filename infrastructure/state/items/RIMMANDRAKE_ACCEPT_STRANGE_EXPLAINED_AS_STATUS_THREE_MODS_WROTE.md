# RIMMANDRAKE_ACCEPT_STRANGE_EXPLAINED_AS_STATUS_THREE_MODS_WROTE

Caused by RIMMANDRAKE_ROUTE_PYRELANDS_VISIT_TWO_FAILURES_BACK (steward run, Pyrelands in-game visit 2, 2026-11-21).

## spec

`_strange_settled` in `src/RimMandrake/rimflow/maturation.py` read an entry as explained only from an `explained`
field. The drivers of Pyrelands (visit 2), FlowWorks (visits 1, 2) and ExplosiveKnockback (visits 1 to 3) wrote
`{"status": "explained", "why": ...}` or `{"status": "explained", "note": ...}`. So Pyrelands visit 2 read 10 strange
things as neither explained nor filed, and its block's `strange_open: 0` as false. This is a fault of form, so the
reader repairs it: with `status` explained and no `explained` field, the reader reads `why`, else `note`. The word floor
(EXPLAIN_WORDS) still binds. A bare status explains nothing.

## verify

`python3 src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py` (test
`strange-explained-as-status-settles`). Seen red on the parent, green on the fix.

## criteria

- `{"status": "explained", "why": <6 words or more>}` and the same with `note` are settled.
- `{"status": "explained"}`, a short `why`, or a `why` without the status are not settled.

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py`, exit 0, 17 tests.
