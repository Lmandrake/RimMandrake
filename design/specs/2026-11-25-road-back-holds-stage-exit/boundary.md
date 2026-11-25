# Boundary: a road back holds the stage it sends a mod to

Code: `road_back_hold`, `move_item` and the `road_back_items` clause of `evaluate` in
`src/RimMandrake/rimflow/maturation.py`. Tests: `src/RimMandrake/rimflow/selftest_maturation_road_back_hold.py`.
Item: `RIMMANDRAKE_HOLD_MOD_AT_ROAD_BACK_STAGE_AND_LET_BUNDLE_BRIEF_START`. On 2026-11-25 at 10:00 AM PST the steward sent
Explosive Knockback 0.2.0 from in-game acceptance back to the offline build. `maturation.py next` then printed that
every exit test of the offline build passed, while the repair items of that road back were open.

## ACCEPTS (the only inputs this is built for)

- **a-stage-record-with-moves.** `version/stage_record.json` whose `moves` list holds dicts with `from`, `to`, and
  `item` or `unit` (a move written before this page has only `unit`).
- **the-sharded-ledger.** `infrastructure/state/ledger/events/*.jsonl`, read by `ledger_items_caused_by` and
  `ledger_ended`.

## DOES NOT SURVIVE (not promised)

- **items-named-nowhere.** A repair item that is neither filed caused_by the move's item nor named in the move's why
  or steward words is not found.
- **a-ruling-id-in-the-why.** A ledger item id in the move's why that is not a repair (a cited ruling that is itself an
  open item) holds the mod like a repair item.
- **an-older-road-back.** Only the newest move counts. A mod that moved on and came back again reads its newest road
  back only.

## LIMITS

None.

## PROMISES (each one is owed a test of the same name)

- **an-open-repair-item-holds-the-stage-exit.** When the newest move went to an earlier stage and the record still
  stands there, the forward exit refuses (clause `road_back_items`) while a repair item is open. The refusal names each
  open item with its needs. The items are those filed caused_by the move's item (the move's `item`, else its run
  record's item through `unit`) and the ledger items that the move's why names.
- **closed-or-dropped-items-do-not-hold.** A closed, dropped or superseded item does not hold. A reopened item (a
  `live` event with result broken after the close) holds again.
- **a-live-only-item-does-not-hold-an-offline-stage.** At an offline stage, an item whose needs is game-up or bridge is
  Stage 6 work: the refusal names it as such, and it does not hold. At Stage 6 and later it holds.
- **an-item-that-cannot-be-read-holds-and-says-could-not-look.** A ledger folder that is missing or cannot be read, and
  a run record that cannot be read for the move's item, hold the exit, and the refusal says "could not look".
- **a-forward-move-or-another-stage-holds-nothing.** A record whose newest move went forward, or that no longer stands
  at the road back's stage, gets no `road_back_items` clause.
- **advance-writes-the-item-of-the-run-that-moves.** `advance` writes `item` on each move: the item of the run named by
  `RM_ROLE_UNIT`, or None for a hand move.
