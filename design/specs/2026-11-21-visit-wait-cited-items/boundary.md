# BOUNDARY: the road back after a visit waits on the items its failed lines cite, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`visit_cited_items`, the `named` reader of `ledger_items_caused_by`),
`src/RimMandrake/rimflow/maturation_autonomy.py` (`open_road_back`, `road_back_open`, `_road_back`) and
`src/RimMandrake/rimflow/maturation_dispatch.py` (the pilot launch and holder reads of the road back). Item
`RIMMANDRAKE_FIX_VISIT_WAIT_MISSES_FAILURE_CITED_ON_OLD_ITEM`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py`.

The case (2026-11-21, FlowWorks visit 5): the driver put its `sc_hung_bridge` FAIL line on
`GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO`, an item filed on 2026-10-23 with no `caused_by`. The road back waited only on
items caused by the driver or the steward run, so visit 6 would have launched without the fix. The steward run caught it
by hand.

## ACCEPTS

- **rows-with-filed.** A visit's `rows.jsonl` row names its item in `filed` or in `owner`, as one rimflow item name or
  a list of them. A name that is not a rimflow item name is ignored.
- **road-back-opened-at-a-steward-launch.** The tick opens the road back when it launches a steward after an in-game
  visit; the row carries `stage: in_game` and `visit: N`, and the visit's `rows.jsonl` is in the tick's clone.

## DOES NOT SURVIVE (not handled)

- **rows-written-after-the-steward-launch.** The cited items are read once, when the road back opens. A failed line
  that names an old item and lands after that is not waited on.
- **a-road-back-opened-before-this-page.** A road back open before this change has no `cited` field and waits on its
  caused-by items only.
- **a-cited-name-with-no-ledger-event.** A cited name that no ledger event carries is not an open item: nothing waits
  on it.
- **the-blind-cycle-rows.** A blind cycle's rows are not read for cited items.

## PROMISES (each one is owed a test of the same name)

- **failed-line-on-old-item-holds-the-next-visit.** When every item caused by the driver or the steward is closed and
  an open item that a failed line of the visit names was filed with no such cause, `_road_back` decides the row, its
  fixer goes to that item, and the road back stays open.
- **closed-cited-item-holds-nothing.** When the cited item is closed or superseded, the road back of a moved mod
  closes.
- **only-failed-lines-are-cited.** `visit_cited_items` takes `filed` from rows whose verdict is not PASS, as a name or a
  list of names, rimflow item names only.
- **owner-named-item-is-cited.** A failed row that names an item only in `owner` cites it, like `filed`; a PASS row's
  `owner` cites nothing (Pyrelands visit 5, 2026-11-22: `sc_grass_regreens` named its old item only as `owner`, and the
  road back left it out).
- **unreadable-visit-record-is-said.** When the visit's `rows.jsonl` cannot be read, the road back opens on the
  steward item and records `cited_unread` naming `rows.jsonl`; it never records an empty cited list.
