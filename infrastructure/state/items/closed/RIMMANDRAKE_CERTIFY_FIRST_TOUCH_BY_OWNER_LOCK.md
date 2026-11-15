# RIMMANDRAKE_CERTIFY_FIRST_TOUCH_BY_OWNER_LOCK

## Defect
MATURATION_NOW listed "Graffiti Framework: GRAFFITI_DESIGN_FIRST_TOUCH on his list" under Needs Mandrake after he had
locked Graffiti 0.1.0 himself by card (2026-11-15 11:33 AM PST, "Lock as 0.1.0 now"; the card said its design stage
had finished; `design/concepts/Graffiti/version/VERSION.json` locked_by owner). delegation_policy §2.7 reserves only the
certification sitting; his lock of the version that pass produced is that certification. owner_queue kept the row his.

## Fix
`owner_queue.read_certified()` / `certified_ids()`: a first-touch row whose concept folder holds VERSION.json
state locked AND locked_by owner leaves his list and is named under `certified` (the CLI prints "close them").
A pipeline lock (new mods lock at 0.1.0 by the pipeline), a draft, a garbled or absent VERSION.json certify nothing;
an unreadable root keeps every row his. GRAFFITI_DESIGN_FIRST_TOUCH closed on that reading.
Left: no page line yet tells the Conductor to close a future certified row; the CLI lists it.

## Acceptance test
`python3 src/RimMandrake/Utils/selftest_owner_queue.py` -> `RESULT GREEN (0 fail)`. On base 0c28b2596e it crashed
(no `read_certified`, watched); a mutant that lets a pipeline lock certify turns "his lock certifies; ..." red (watched).
Real-books check: no listed first-touch row is one his lock already certified.
