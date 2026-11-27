# RIMMANDRAKE_LET_CLEAR_PASS_CHAIN_STOP_THREE_CLEARS_NO_LAUNCH

## spec

At 5:54 AM PST 2026-11-27 the Conductor ran `list_dispatch.py clear <ID> --why "..."` on three tickets whose lane row
read `chain_stop`. Each call printed `CLEARED <ID>: the next tick may launch one more run`. At 6:45 AM PST all three
still read `chain_stop` and no run had started. The `clear` command only empties the item's `attempts` in
`state.json`; the chain gate reads the item's `depth` against `max_chain_depth` and never reads `cleared`. So the
chain stop's printed path to pass does nothing.

The work: a `clear` by a hand grants ONE lane run past the chain stop for that item. The grant is spent when that run
launches. After that run, the item reads `chain_stop` again unless it is cleared again. Items that nobody cleared keep
the chain rule unchanged. Check every other stop kind that prints `clear` as its path to pass, and repair it the same
way if `clear` does not lift it.

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_list_dispatch`, with new cases for the chain grant.

## criteria

- An item at the chain limit with a `cleared` record newer than its last run launches once.
- The tick after that launch reads `chain_stop` again.
- An item never cleared still reads `chain_stop`.
- A `cleared` record older than the item's last run grants nothing.
- A `state.json` with no `cleared` key works as before.

## refs

file: src/RimMandrake/rimflow/list_dispatch.py
file: src/RimMandrake/rimflow/selftest_list_dispatch.py
file: design/specs/2026-11-23-list-dispatch/boundary.md
