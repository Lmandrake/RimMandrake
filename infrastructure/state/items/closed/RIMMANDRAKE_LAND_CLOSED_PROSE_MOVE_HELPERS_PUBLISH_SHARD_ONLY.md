# RIMMANDRAKE_LAND_CLOSED_PROSE_MOVE_HELPERS_PUBLISH_SHARD_ONLY

## spec

A failure that happened (test 1 of `standing_rulings.md` §Touching code has a cost: a failing test).
`src/RimMandrake/rimflow/selftest_items_glob_live.py` is red on origin/main, measured 2026-11-19 about 6:55 PM PST at
f48b559cd5: five items are `done` in the ledger but their prose is still in `infrastructure/state/items/`, not
`items/closed/`:
ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING, AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO,
CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES, RIMMANDRAKE_RETIRE_TODOIST_AS_ALERT_ROUTE_IT_NEVER_RANG,
RIMMANDRAKE_SCOPE_SELFTEST_LEDGER_READS_PREFLIGHT_LOG_TRIPS.

Cause, read from the code: `cli.py` `_move_prose_to_closed` renames the file on the closing clone's disk and leaves the
commit "for the caller". Every one of the five was closed by seat CONDUCTOR (four in the old-era ticket sweep,
2026-11-18 23:18 to 23:22Z; one by a detached run, 2026-11-19 14:33Z). Those runs publish only their ledger shard
(the detached brief's own close step names only `infrastructure/state/ledger/events/<SEAT>.jsonl`), so the rename
never lands. A hand `git mv` of the five would hide the cause, and the pipeline rule forbids a hand workaround without
the permanent fix.

Why it was set down, not fixed (test 2 evidence): the enacting run's brief barred code edits; the permanent fix is a
choice (close commits the move itself; or `./publish` and `land.sh` carry a pending prose move; or the detached
brief's close step names the moved paths), in pipeline machinery whose boundary page must come first.

## criteria

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_items_glob_live.py` exits 0 on origin/main (red at filing:
5 drifted), AND a new case in a selftest closes a fixture item from a clone and publishes the way a detached helper
does, then reads the prose under `items/closed/` on the published commit. Watched red at filing: the first half
(5 drifted); the second half does not exist yet and is part of the fix.
