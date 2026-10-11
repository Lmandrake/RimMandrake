# FlowWorks P-series — picker AG, 2026-10-11 (FOUNDRY)

Takes the HIGHEST unclaimed offline-provable P item (AF takes the lowest). P14 and P10 were done earlier; P4 is with AF.

## P11 STATION_REACH_CENTRE_RETHINK_FOOTPRINT
**Defect (verified):** `src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs` `ReachCells()` took a
circle of `reach + rect.Width/2` about `Position`. On the 3×2 pumping station (reach 4) that reached 5 cells off the
bottom edge and 4 off the top, and the footprint's height was never used.

**Fix:** `RM_PumpMath.FootprintDistSq` / `InFootprintReach` (Verse-free) measure from the footprint's nearest cell;
`ReachCells` scans `rect.ExpandedBy(ceil(reach))`, keeps cells within reach, nearest first. Touching-cell pumps
(reach ≤ 1.5) unchanged.

**Proof (offline):** `PrePortFixChecks.cs` case `P11_station_reach_is_measured_from_the_footprint` (4 off every side
in, 5 out, footprint excluded, corner bound) plus a can-fail: the old circle reaches (10,5), the new rule does not.
`selftest_flowworks_stock.py` 160/160; rivers/swale/cover_breaks/looks_round pass; `winbuild.py FlowWorks` 0 errors.
Owed live: a station drawing from water 4 off its long side in game. Not deployed.
