## spec

A locked-change chain steward gives the concept ONE coverage look; a not_covered look stops judging, and the steward
files the gaps as fix items caused by its own item (its brief says so, "so the tick finds and fixes them"). But
`maturation_autonomy.stop_tickets` found only the grant's items, the road back's (a chain steward opens none) and fix
items caused by the concept's own item, so a coverage-stopped mod's chain-filed fixes got no fixer run and the mod sat
PAUSED with its tickets unseen (Graffiti, 2026-11-17).

Fix: stop_tickets also takes the open fix-kind items caused by any chain steward item in the mod's steward book
(key `<ver>|chain|<at>`), after the concept's own.

## criteria

A coverage-stopped mod's chain steward's open fix tickets are its stop tickets; another steward's are not.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py` ALL PASS; its "paused-fix: the default
reader finds a chain steward's own fix tickets" check failed before the fix (read ['FIX_K']).
