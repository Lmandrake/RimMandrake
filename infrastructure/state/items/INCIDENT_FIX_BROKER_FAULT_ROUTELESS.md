# INCIDENT_FIX_BROKER_FAULT_ROUTELESS

## proof (corrected 2026-11-17, drain of the retired judge)
    python3 src/RimMandrake/rimflow/selftest_incident.py

## what it reads, measured 2026-11-17 — rc=1, and the reds are NOT this item's
Two checks are red, and neither is the broker-fault routing this item is about:

1. `FAIL no alarm site in the tree is unreadable by the census` →
   `['Utils/ops_watch.py:1084 point key Name', 'Utils/ops_watch.py:1090 point key Subscript']`
   The alarm census cannot read two of its own call sites, because the point key there is an expression
   (an attribute/subscript) rather than a literal.
2. `FAIL every role_launch alarm falling through to cause roles is a reviewed fault (new: ['codex_stop'])`
   A new alarm name, `codex_stop`, reaches the cause roles without a review entry.

Both are real faults in the shared alarm machinery that this selftest also guards; the honest reading is that
the file is red, so the item does not close. Evidence:
/Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/INCIDENT_FIX_BROKER_FAULT_ROUTELESS.txt

Next worker: fix the two faults above (teach the census to read an expression point key, and review or route
`codex_stop`), re-run the line, and only then judge the broker-fault routing this item names.
