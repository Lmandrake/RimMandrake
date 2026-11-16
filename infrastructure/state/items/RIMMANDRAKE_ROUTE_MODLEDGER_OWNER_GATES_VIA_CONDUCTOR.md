# RIMMANDRAKE_ROUTE_MODLEDGER_OWNER_GATES_VIA_CONDUCTOR

## spec
Measured 2026-11-16 ~07:00 PST in the BENCH clone (HEAD before 9d0451b34a): `run_selftests.py --only
selftest_conductor_authority` is RED, on files the measuring change did not touch:
- `src/RimMandrake/rimflow/modledger_backfill.py`: compares to "OWNER" (line 296) in a file with no Conductor route
  and no OWNER_ONLY entry;
- `src/RimMandrake/rimflow/modledger.py`: his words with no route, line 2034 (a).
Both files changed in the modledger miner round 4 commits (302a79ea40, 16bd3747c2, about 3-4 h earlier).
Evidence: `D:\ClaudeWork\rimmandrake\scratch\dead_owner_lock\conductor_authority_red.txt`.

## criteria
(a) Each gate in modledger.py / modledger_backfill.py that tests his words or seat OWNER carries the Conductor's
route (CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM) or is listed OWNER_ONLY with its ruling. (b)
selftest_conductor_authority is green.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_conductor_authority`

## refs
file: src/RimMandrake/rimflow/modledger.py
file: src/RimMandrake/rimflow/modledger_backfill.py
file: src/RimMandrake/rimflow/selftest_conductor_authority.py
