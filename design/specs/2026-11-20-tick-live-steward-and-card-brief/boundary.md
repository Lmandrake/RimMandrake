# BOUNDARY: the tick waits on its own live steward run, and its briefs carry a by-card item's card (maturation_autonomy.py _gate, resolve, card_brief, launch_brief), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_autonomy.py` (`_gate` with its `live` argument, the `_gate` call in `resolve`,
`card_brief`, `launch_brief`). The `_gate` part landed first under item
`RIMMANDRAKE_SEE_LIVE_STEWARD_BEFORE_CALLING_IT_SPENT` (its tests in `selftest_maturation_autonomy.py`); this page's tests
read it again at the stage where it was measured. **This page covers only two things: the reading of a booked steward or fixer run that is
still live, and the card text in a brief that the tick launches.** Item
`RIMMANDRAKE_FIX_FLOWWORKS_FAULT_LOOP_AND_SLACK_STEWARD_MISREAD`. Measured 2026-11-20:

- GimmeSomeSlack at preflight read `steward_spent` ("ended and the state has not moved") while its steward unit
  `rm-detached-bench-rimmandrake-steward-gimmesomeslack-prefl-1795220569` was systemd `active/running` and the tick's
  own facts listed it in `live_units`. At a stage other than `offline_build`, `maturation_dispatch.decide` reads
  `not_offline`, never `live`, so `resolve` routed the steward row and `_gate` read the booked key as an ended run.
  A hand `clear` on that reading would have launched a second steward beside the live one.
- FlowWorks read `system_fault` after three launches of the fixer on the by-card item
  `RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN`: `detached_helper.py launch` gate I3 (`card_refusal`) refused
  each brief, because no brief builder of the tick pastes the picked option's description.

Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_tick_live_steward_card_brief.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-booked-run.** `st["mods"][mod]["steward"|"fixers"][key]` as `execute` books it: `unit` (a unit name or None),
  `failed`, `tries`.
- **a-live-list.** The mod's `live_units` from `maturation_dispatch.gather`: a list of unit names, or `UNMEASURED`
  (not a list).
- **a-tick-brief.** The brief text that `launch_brief` receives, and the item it is for. The item's cards are the
  `card` fields of its ledger events (`card_capture.item_cards`).

## DOES NOT SURVIVE (not handled)

- **an-unreadable-live-list.** When `live_units` is not a list, `_gate` reads the booked run as before (spent). The
  dispatch rows already read `blind` on an unreadable run store at `offline_build`; other stages are not changed here.
- **a-card-store-that-raises.** An events shard that cannot be read raises out of `launch_brief`. `execute` books that
  row `launch_failed` with the exception's text.

## PROMISES (each one is owed a test of the same name)

- **live-booked-run-reads-live.** When the booked run's unit is in the live list, `_gate` returns
  `(False, ("live", ...))`, the text naming the unit. It never returns `steward_spent` or `fixer_spent` for it.
- **ended-booked-run-stays-spent.** When the booked run's unit is not in the live list (or no list is given), `_gate`
  returns `steward_spent` as before.
- **resolve-waits-on-live-steward-at-preflight.** `resolve` on a preflight row whose booked steward unit is live gives
  decision `live`, no `aut`, `waits_on` naming the unit, klass `wait`, and no launch.
- **card-brief-carries-picked-description.** `card_brief` on a by-card item appends `## What the card said` with each
  card as `card_capture.flatten(card, brief=True)` gives it, and the result passes `detached_helper.card_refusal`.
- **card-brief-leaves-other-briefs-alone.** A brief for an item with no card, or a brief that already carries every
  picked description, comes back unchanged.
- **launch-brief-writes-the-card.** The brief file that `launch_brief` writes for a by-card item holds the picked
  description, so the launch's gate I3 does not refuse it.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
