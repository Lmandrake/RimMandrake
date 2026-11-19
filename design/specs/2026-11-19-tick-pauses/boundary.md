# BOUNDARY: the Maturation tick's Designer-block pause, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_autonomy.py` (`blocked_closed`, `_stop_tickets` on `kind="blocked"`,
`unblock_and_land`, `execute`'s `autounblock` act) and `src/RimMandrake/rimflow/maturation_dispatch.py` (`NO_SLOT_AUT`,
`_launch_kind`). **This page covers only the pause a Designer block makes.** The other tick decisions have their own
pages (`2026-11-19-stage-ceiling`, `2026-11-19-void-counters`, `2026-11-19-consumable-readers`). Item:
`RIMMANDRAKE_LIFT_DESIGNER_BLOCK_NAMING_DONE_ITEM_SLIME_WAITS`, written 2026-11-19 by
`RIMMANDRAKE_FIX_CONTROL_STORE_COUNTS_AND_TICK_PAUSES`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_tick_pauses.py`.

The case: GelatinousSlime's `stage.json` reads `blocked` on `RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS: ...` since
2026-11-16 08:55 PST, and that item is done. `blocked_tickets` finds no open ticket in the reason, so the tick paused
the mod with no next act and nobody's name on it.

## ACCEPTS (the only inputs the code is built for)

- **a-reason-that-names-items.** A Designer's `blocked_on` text that names ledger items by id (`ITEM_NAME`). A reason
  that names none is a plain pause, as before.
- **a-readable-ledger.** The ledger replays (`ledger_items`). An unreadable ledger leaves the plain pause.

## DOES NOT SURVIVE (not promised)

- **a-lift-whose-landing-fails-after-the-write.** `unblock_and_land` puts `stage.json` back byte for byte when the
  landing raises. A landing that pushes and then reports failure is booked as a failed try; the next tick reads the
  pushed `ready` concept and routes it normally.
- **a-reason-that-names-a-closed-item-and-something-else.** A reason may name a closed item and also a condition that
  is no item (a brief that is UNTESTED, a missing signature). The lift does not judge that condition: the Designer's
  next run at the same stage re-reads its own gate, and blocks again if the condition still stands. The second block
  is not lifted (next promise).

## PROMISES (each one is owed a test of the same name)

- **block-on-closed-items-lifts-once.** A blocked Designer whose reason names at least one ledger item, every named
  item closed (done, dropped or superseded), and no open fix ticket, is lifted by the tick as an act (`autounblock`:
  no brief, no run, no slot, one landing of `stage.json`), booked under its steward key
  (`<version>|unblock|<reason hash>`). The row says which closed items it named.
- **a-second-block-on-the-same-reason-names-what-is-owed.** When the same reason stands again after the tick lifted
  it once, the tick does not lift it again: the mod stays PAUSED, and `why` and `need` name the closed items, the
  time of the earlier lift and the hand command (`designer_stage.py unblock`).
- **an-open-or-unknown-item-is-no-lift.** A reason that names an open item (its fixer run is `_stop_tickets`'s) or an
  id the ledger does not hold is not lifted.
- **a-failed-lift-puts-stage-json-back.** A landing that raises leaves `stage.json` byte for byte as it was, and the
  row reads `launch_failed` with the error.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
