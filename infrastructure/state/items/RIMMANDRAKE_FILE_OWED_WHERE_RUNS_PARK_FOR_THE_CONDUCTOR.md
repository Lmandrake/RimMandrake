## spec
Ticket 4 of design/specs/2026-11-15-conductor-restart-loses-nothing.md (in build order 1-4). Build E3 of `design/specs/2026-11-15-conductor-restart-loses-nothing.md` §3, narrowed by GPT's read (§4), after ticket 1. `python3 src/RimMandrake/rimflow/owed.py
sync-sources`, run by the Dispatcher tick, files one owed item per explicit Conductor hand step the programs already
name. Those are a maturation row whose next says "the Conductor decides" (three blind cycles) or "a card in the
Conductor log", and a detached record carrying `owed_close` whose item is still open. Each item is keyed by its source
(`maturation:<mod>@<version>:<stage>:visit<n>`, `detached:<unit>`) and serialized through the ledger writer, so two
concurrent runs file each key once. Plain failed runs are not sources.

Measured why (spec §1 row 26, §2 M3): "Gimme Some Slack is paused for the Conductor's call" reached the Conductor only
as a run result, after the window that launched it was gone.

## refs
item: RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/dispatcher.py
file: src/RimMandrake/rimflow/owed.py
file: src/RimMandrake/rimflow/acceptance/owed_sources_accept.py
file: design/specs/2026-11-15-conductor-restart-loses-nothing.md

## verify
python3 src/RimMandrake/rimflow/acceptance/owed_sources_accept.py

## criteria
- A1: the acceptance test prints `PASS 10/10` and exits 0.
- A2: no other selftest of the touched files goes red (`run_selftests.py --only` on them), and the close note says which ran.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/owed_sources_accept.py` exits 0 with `PASS 10/10`. Watched failing on base `0639e8226d` (2026-11-15, BENCH detached
run): `FAIL 2/10`, exit 1. The builder does not edit the test; a clause no correct build can meet goes to the Conductor.
