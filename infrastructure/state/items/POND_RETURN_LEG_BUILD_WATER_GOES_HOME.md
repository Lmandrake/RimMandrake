# POND_RETURN_LEG_BUILD_WATER_GOES_HOME

Spec: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` §4 Option A, §7 net change; owner rulings
5 and 6 (2026-10-12, same file, "Owner rulings").

## built (BENCH night helper, 2026-10-13, offline)

- **Return leg (G1, GPT #5/#6).** `RM_MapComponent_Excavation.CanReturnLevels / TryReturnLevels`: a natural pond square
  or its dried bed square (never a dug one) takes whole levels back into the pond's stock, all or nothing, up to
  capacity, through `RM_LiquidStock.CreditLevels`; a foreign fluid is refused before anything changes; never forms a
  body. Limitless bodies take any level (counted as an exit, `toLimitless`).
  - Pump on Pour: dug cells in reach first, then a pond in reach (`Building_LiquidPump.PourToPond`), then outflow ends.
  - Outflow ends: `RM_LiquidSpill.Outlet` returns the new `RM_OutletKind.Body` (appended last) when no dug cell takes
    the level but a pond square or bed at/next to the end does; checked before water terrain is called Blocked.
    `RM_LiquidSpill.OutletLeg` is now the one world leg for the pump's world-to-world move, its pour and the Dump drain.
  - The world-to-world undo of a pond draw now puts back a whole level via `CreditLevels` (was a partial `TryCredit`).
- **Honest selftest (G2).** `Pump_pond_round_trip_conserves` (hand-written `pond++`) replaced by
  `Pump_pond_round_trip_production`: production `CanDebit` / `CreditableLevels` legs plus the production call sites.
  The conservation model's gap detector now follows TryPour → PourToPond → Body leg → TryReturnLevels → CreditLevels;
  trip 6 flipped from "documents the gap" to demanding the full round trip, and passes.
- **Refill guard (ruling 5, GPT #12).** `Restore` skips a receded square holding a pawn or a building (frames count,
  blueprints do not) and puts it back on TOP of the stack for the next pulse; items there are moved to the nearest dry
  shore square that is not a pond or a dig; an item that cannot be placed is put back and the square waits.
- **Checked Restore (GPT #11).** `RestoreOriginalTerrain` returns `RM_RestoreResult`; the record is removed only after
  the write is seen. A write that did not take is retried next pulse; a square with no record is dropped with a warning.
- **G5 / ruling 6.** The first cut into a DRY bed square detaches it from its pond (footprint, receded list, its exact
  capacity share); the natural-bed record `RM_detachedBedCells` is scribed. Filling it back in to the surface returns it
  to the pond as dry bed (Mud) and restores its share — it no longer writes unpaid lake water. Share arithmetic is
  `RM_StockMath.CapacityWithoutBed / CapacityWithBed` (exact inverse, selftested). Stock above the shrunk capacity
  (only possible for a partly-funded last square) is disclosed through `NotifyOverflowDestroyed`.
- **Truncated-index persistence (GPT #19).** Cells a re-walk adds to a TRUNCATED (limitless) body are saved in its
  footprint; limited footprints stay fixed (ruling 16).
- **L0 ledger probe (G10).** `RM_MapComponent_Excavation.LedgerReport()` and the dev action "Report water ledger (L0)":
  limited body stock, canal levels, tank units, hose held units in tank units, plus exits (destroyed, sunk, burned —
  new `RM_burnedLevelsTotal`, spilled this session, returned to limitless).
- Mod Settings: "Pumps and outflows can refill natural ponds", "Returning water waits for people and buildings",
  "Digging a dried bed takes the square out of its pond" (all on; off = old behaviour).

## not built here

- Recession sparing pump-reach cells (GPT #3, §7 item 2) is not in this item's title; not done.
- A bridge tool for the L0 ledger (JawaBench lives outside FlowWorks); the dev action is the probe for now.
- A stopped hose's drain (`DrainHeld`) still pours only into channels, not ponds.
- Code review: changed files are DIRTY (not self-marked).

## criteria
- O1 L0: `Pump_pond_round_trip_production`, `Pond_dug_bed_leaves_and_returns_exactly`, `Pond_restore_is_checked_and_waits_for_occupants`, `Pond_truncated_index_persists_and_ledger_probe_exists`, `Transfer_caller_coverage` pass (selftest_flowworks_stock.py 291/291)
- O2 L0: conservation model trip 6 demands and passes the natural-pond round trip (13/13); FlowWorks --only sweep 23/23 GREEN
- A1 L2: L3 live: a ~20-cell limited pond drained by a pump into tanks, tanks into a dug B, back into tanks, then Pour/Outflow toward the pond: the pond's wet set equals the snapshot and the L0 ledger total is unchanged within 1e-3
- A2 L2: L6 live: a colonist and a building on dry bed squares delay refill of those squares only; an item on a bed square ends on dry shore
- A3 L2: dig a dry bed square, fill it back in: it is Mud (not water), the pond capacity returns to its value, and the square re-wets on refill
