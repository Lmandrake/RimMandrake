## spec
Ticket 1 of design/specs/2026-11-15-conductor-restart-loses-nothing.md (in build order 1-4). Build E1 of `design/specs/2026-11-15-conductor-restart-loses-nothing.md` §3: the owed view. An owed act is an ordinary item, `rimflow file <ID> --for BENCH --kind owed`
(`--caused-by` the item it acts on). `rimflow queue CONDUCTOR --owed` prints only those that are open: a count line,
the actionable ones oldest first with LATE past 2 h, then WAITING with each `wait` trigger, at most 40 lines. Closing an
owed item needs evidence (a sha, a run id, a path or `told him at <time>` in `--no-code`), and `rimflow next` never
offers one to a builder. `seat_restart.py wake` and `handoff.py --wake` print the view after the old reply. The role
file's Start of turn (`src/RimMandrake/rimflow/roles/conductor.md`) reads it first, and the per-prompt notice in
`.claude/hooks/conductor_goodbye.py` carries its first line.

Seed the two debts measured open at filing as owed items: launch
`RIMMANDRAKE_REALIGN_FLOWWORKS_PROOFS_AFTER_UNDER_LIQUID_LAW` (promised 2026-11-14 10:44 AM PST, never launched), and
hunt the run that writes into `/home/mandrake/rm/bench` (`RIMMANDRAKE_HARDEN_PIPELINE_WHERE_HANDS_CLEANED_UP`'s NEXT,
read by two wakes, unacted).

Measured why (spec §1–2): every wake read `queue CONDUCTOR | tail -40` of a 23,872-line view, and 8 of 9 lost or late
debts had no item saying the Conductor owed the act.

## refs
item: RIMMANDRAKE_STOP_CONDUCTOR_RESTARTS_LOSING_ITEMS_ASK_GPT
file: src/RimMandrake/rimflow/cli.py
file: src/RimMandrake/rimflow/render.py
file: src/RimMandrake/rimflow/priority.py
file: src/RimMandrake/rimflow/seat_restart.py
file: src/RimMandrake/Utils/handoff.py
file: .claude/hooks/conductor_goodbye.py
file: src/RimMandrake/rimflow/roles/conductor.md
file: src/RimMandrake/rimflow/acceptance/owed_view_accept.py
file: design/specs/2026-11-15-conductor-restart-loses-nothing.md

## verify
python3 src/RimMandrake/rimflow/acceptance/owed_view_accept.py

## criteria
- A1: the acceptance test prints `PASS 17/17` and exits 0.
- A2: no other selftest of the touched files goes red (`run_selftests.py --only` on them), and the close note says which ran.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/owed_view_accept.py` exits 0 with `PASS 17/17`. Watched failing on base `0639e8226d` (2026-11-15, BENCH detached
run): `FAIL 2/17`, exit 1. The builder does not edit the test; a clause no correct build can meet goes to the Conductor.
