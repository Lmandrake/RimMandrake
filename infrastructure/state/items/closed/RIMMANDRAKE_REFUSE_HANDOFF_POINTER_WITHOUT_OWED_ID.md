## spec
Ticket 2 of design/specs/2026-11-15-conductor-restart-loses-nothing.md (in build order 1-4). Build E4 of `design/specs/2026-11-15-conductor-restart-loses-nothing.md` §3, after ticket 1: `python3 src/RimMandrake/rimflow/owed.py check-pointers <handoff.md>`. It is a
validator that writes nothing. A `- \`ID\` … NEXT:` pointer must cite an open `kind: owed` id (its own id counts),
and a pointer citing a closed one is refused. `handoff.py --check` runs it. The handoff skill's pointer form
(`~/dev/Lodestar/docs/HANDOFF.md` is Lodestar's; change only RimMandrake's own check) gains "file the owed item, then
cite it".

Measured why (spec §2 M2): a pointer's NEXT is often a relay or decision, and when the pointer's item closes the wake
reads it CLOSED. In the 15:28 handoff, 3 of 15 pointers named items already done.

## refs
item: RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE
file: src/RimMandrake/Utils/handoff.py
file: src/RimMandrake/rimflow/owed.py
file: src/RimMandrake/rimflow/acceptance/owed_pointers_accept.py
file: design/specs/2026-11-15-conductor-restart-loses-nothing.md

## verify
python3 src/RimMandrake/rimflow/acceptance/owed_pointers_accept.py

## criteria
- A1: the acceptance test prints `PASS 7/7` and exits 0.
- A2: no other selftest of the touched files goes red (`run_selftests.py --only` on them), and the close note says which ran.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/owed_pointers_accept.py` exits 0 with `PASS 7/7`. Watched failing on base `0639e8226d` (2026-11-15, BENCH detached
run): `FAIL 0/7`, exit 1. The builder does not edit the test; a clause no correct build can meet goes to the Conductor.
