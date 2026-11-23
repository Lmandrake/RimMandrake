## spec

Design Version: FlowWorks 0.2.0 (next, Divergent or Polish; moves no 0.1.0 bar). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks 0.2.0: pin four laws no test watches (toss range and relight, fetch fire window and key, drill power when off, coating on colonists).

## merged tickets

- `RIMMANDRAKE_PIN_FLOWWORKS_TOSS_RANGE_AND_RELIGHT_UNWATCHED` (proposed): Polish: toss-flame range (provisional 4.9) and no-relight are unpinned
  - sweep reading: self-labelled Polish by the blind-cycle judge 2026-11-16: provisional range 4.9 and no-relight unpinned
  - its check: selftest pins toss range and no-relight
- `RIMMANDRAKE_PIN_FLOWWORKS_FETCH_FIRE_WINDOW_AND_KEY_UNWATCHED` (proposed): Polish: fetch-fallen under-fire window, warning key and interruptible flag unpinned
  - sweep reading: self-labelled Polish by the blind-cycle judge 2026-11-16: under-fire window, warning key and interruptible flag unpinned
  - its check: selftest pins the fetch-fallen under-fire window, warning key and interruptible flag
- `RIMMANDRAKE_NOTE_FLOWWORKS_DRILL_DRAWS_POWER_WHEN_OFF_UNPINNED` (proposed): FlowWorks (Polish, Stage 6 inv_settings): no offline test catches a liquid drill drawing power while switched off or off in Mod Settings (blind cycle 3, planted CALLER_DRILL_DRAWS_POWER_SWITCHED_OFF)
  - sweep reading: Labelled Polish by blind cycle 3 (Stage 6 inv_settings). It is a test gap: the planted CALLER_DRILL_DRAWS_POWER_SWITCHED_OFF goes uncaught offline. No observed failure, no red test; no commit names it
- `RIMMANDRAKE_NOTE_FLOWWORKS_COATING_LAWS_MISS_COLONISTS` (proposed): FlowWorks (Polish, Stage 6 inv_liquid_coating): the coating source laws stay green when colonists are never coated or a dug canal's liquid never coats (blind cycle 3, planted COAT_COLONISTS_NEVER_COATED, COAT_CANAL_LIQUID_NEVER_COATS)
  - sweep reading: self-labelled Polish in item; coating laws exist (inv_liquid_coating bar)
  - its check: coating proof includes a colonist case

## his words (as recorded on the merged tickets)

- none recorded on these tickets

## verify

Acceptance test: none as one command, 0.2.0 work: each pin is a new law seen red under its planted fault (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_PIN_FLOWWORKS_TOSS_RANGE_AND_RELIGHT_UNWATCHED
item: RIMMANDRAKE_PIN_FLOWWORKS_FETCH_FIRE_WINDOW_AND_KEY_UNWATCHED
item: RIMMANDRAKE_NOTE_FLOWWORKS_DRILL_DRAWS_POWER_WHEN_OFF_UNPINNED
item: RIMMANDRAKE_NOTE_FLOWWORKS_COATING_LAWS_MISS_COLONISTS
