# VENOMVINE_PATHCOST_AND_FLYER_1 — the two venomvine properties still unobserved

## what is wrong

`VENOMVINE_LIVE_VERIFY_1` closed with every step of
`design/Jawa/worldbuilding/desert_shade_plants_design.md` §5 observed except two
things, both of which need a live map and neither of which could be staged on demand.

## 1. step 4 — a flyer crosses a stand and is untouched

`MapComponent_ContactVenom.Sample` skips a pawn when `pawn.Flying`, copied from
`Building_Trap.Tick`. That one line has never been seen doing anything.

🔴 **It cannot be forced, and this is MEASURED, not assumed** (2026-09-21): the whole
debug surface was enumerated — `Settings` (181 children) and `Actions` (360 children) —
and **zero** nodes match fly/flight; no `jawa/` or `rimworld/` bridge tool writes
`Pawn.Flying`. 1.6 flight is a stat-driven state (`Pawn_FlightTracker.CanEverFly`
reads `MaxFlightTime > 0`) that a bird enters on its own via
`flightStartChanceOnJobStart`.

⇒ The only route is **observational**: put a solid vine stand on a map, put many
birds that carry `MaxFlightTime` on it (Core's Chicken/Duck/Goose/Sparrow, or any of
our own flyers), run a long window, and compare their venom accumulation against
ground animals on the same stand. A flyer that crosses grounded will still be
scratched, so the claim is a RATE difference, not a zero — size the sample for that.
⛔ Do not report "the bird was not scratched" from one bird; it may simply not have
stepped on a vine.

## 2. `pathCost 60` in practice

`RM_Venomvine` carries `pathCost 60` so a sparse stand is threaded and a solid band is
detoured when the detour is cheaper — the design's own avoidance rule. Never observed.

Stageable offline-ish on a quicktest map: paint a solid band across a corridor, order a
colonist from one side to the other with `jawa/order_pawn` / `jawa/prioritized_work`,
and read the route taken against the same order with the band removed. Do it at two
band widths so "threaded" and "detoured" are both exercised.

## verify

A measured rate difference for flyers over a stand, with a grounded control on the
same stand; and two recorded routes (threaded, detoured) with the cell lists.

## criteria

Both observed, or each recorded NOT-RUN with the reason measured rather than asserted
— the standard `VENOMVINE_LIVE_VERIFY_1` set.
