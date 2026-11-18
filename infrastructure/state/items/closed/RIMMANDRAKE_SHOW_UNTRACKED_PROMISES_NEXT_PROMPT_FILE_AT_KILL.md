## spec
Ticket 3 of design/specs/2026-11-15-conductor-restart-loses-nothing.md (in build order 1-4). Build E2 of `design/specs/2026-11-15-conductor-restart-loses-nothing.md` §3, advisory (GPT's read, §4), after ticket 1. `src/RimMandrake/rimflow/promise_scan.py` finds
promise sentences: the Conductor's own future or unfinished acts, and a closing question to him. A sentence counts as
tracked only if it names an open owed id. `.claude/hooks/conductor_goodbye.py` shows the last reply's untracked ones
on the next prompt. At a backstop kill, `seat_restart.py` files them as `kind: owed` titled `UNTRACKED promise:
<sentence>`, before the shard publish, and never refuses the kill. No turn is blocked. Record the false-positive count
over the first week of real replies on this item: the blocking decision waits on that number.

Measured why: 6 of the 9 lost or late debts were promises written as prose in ordinary replies (spec §2). The
test's positive cases are those sentences.

## refs
item: RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE
file: src/RimMandrake/rimflow/promise_scan.py
file: .claude/hooks/conductor_goodbye.py
file: src/RimMandrake/rimflow/seat_restart.py
file: src/RimMandrake/rimflow/acceptance/owed_promise_scan_accept.py
file: design/specs/2026-11-15-conductor-restart-loses-nothing.md

## verify
python3 src/RimMandrake/rimflow/acceptance/owed_promise_scan_accept.py

## criteria
- A1: the acceptance test prints `PASS 21/21` and exits 0.
- A2: no other selftest of the touched files goes red (`run_selftests.py --only` on them), and the close note says which ran.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/owed_promise_scan_accept.py` exits 0 with `PASS 21/21`. Watched failing on base `0639e8226d` (2026-11-15, BENCH detached
run): `FAIL 0/21`, exit 1. The builder does not edit the test; a clause no correct build can meet goes to the Conductor.
