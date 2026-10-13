// POND_RETURN_LEG_BUILD_WATER_GOES_HOME (design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md §4 Option A, §7 net
// change; owner rulings 5 and 6, 2026-10-12). The arithmetic is PRODUCTION RM_StockMath; the Verse-bound wiring (dug bed
// detach/reattach, checked and guarded Restore, truncated-index persistence, the L0 ledger) is pinned at its call sites.
// The pump/outflow return leg itself is PumpChecks.Pump_pond_round_trip_production.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PondReturnChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Pond_dug_bed_leaves_and_returns_exactly", () =>
            {
                // a 10 shallow + 10 deep pond (60 levels); a deep bed square is dug out, then filled back in
                float cap = 60f;
                float less = RM_StockMath.CapacityWithoutBed(cap, 4, 60);
                Assert(Math.Abs(less - 56f) < 1e-4, "a deep square takes its 4 levels with it: " + less);
                float back = RM_StockMath.CapacityWithBed(less, 4, 56);
                Assert(Math.Abs(back - cap) < 1e-4, "filled back in, the pond is its old size: " + back);
                // with a budget slider the share is proportional, still an exact inverse
                float scaled = 60f * 0.7f;
                Assert(Math.Abs(RM_StockMath.CapacityWithBed(RM_StockMath.CapacityWithoutBed(scaled, 2, 60), 2, 58) - scaled) < 1e-4,
                    "the share is the square's part of whatever the pond was sized at");
                Assert(RM_StockMath.CapacityWithoutBed(cap, 4, 0) == cap && RM_StockMath.CapacityWithBed(cap, 0, 10) == cap, "degenerate inputs change nothing");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(d == RM_ExcavationDepth\.Surface\) \{ RecordOriginalTerrain\(c\); DetachIfDryBed\(c, i\); \}",
                    "the first cut into a square checks for a dry bed (after the water record is kept)");
                RiverSwitchFlipChecks.Has(ex, @"if \(body == null \|\| !body\.receded\.Contains\(c\)\) \{ return; \}", "only a DRY (receded) bed square detaches");
                RiverSwitchFlipChecks.Has(ex, @"ClearFillTerrain\(c\); if \(!ReattachIfDetachedBed\(c, i\)\) \{ RestoreOriginalTerrain\(c\); \}",
                    "filling a detached bed to the surface returns it to its pond instead of writing unpaid water (G5)");
                RiverSwitchFlipChecks.Has(ex, @"map\.terrainGrid\.SetTerrain\(c, bed\); stock\.ReattachBedCell\(map, body, c, this\);", "it comes back as dry bed");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Collections\.Look\(ref detachedBedCells, ""RM_detachedBedCells""", "the natural-bed record survives a save (GPT #10)");
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"body\.cells\.Add\(c\); body\.receded\.Add\(c\);", "reattached as a receded square, so Restore re-wets it");
            });

            Case("Pond_restore_is_checked_and_waits_for_occupants", () =>
            {
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(map\.terrainGrid\.BaseTerrainAt\(c\) != original\) \{ return RM_RestoreResult\.WriteFailed; \} originalTerrain\.Remove\(i\); bedGrid\[i\] = 0; return RM_RestoreResult\.Restored;",
                    "the record is removed only after the write is seen (GPT #11)");
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"if \(RimMandrakeFlowWorksSettings\.refillWaitsForOccupants && !ClearForRefill\(map, c, body, owner\)\) \{ if \(waiting == null\) waiting = new List<IntVec3>\(\); waiting\.Add\(c\); continue; \}",
                    "an occupied square is skipped, not blocking the stack (GPT #12)");
                RiverSwitchFlipChecks.Has(st, @"else if \(r == RM_RestoreResult\.WriteFailed\) \{ if \(waiting == null\) waiting = new List<IntVec3>\(\); waiting\.Add\(c\); \}", "a failed write is retried");
                RiverSwitchFlipChecks.Has(st, @"for \(int i = waiting\.Count - 1; i >= 0; i--\) \{ body\.receded\.Add\(waiting\[i\]\); \}", "waiting squares go back on TOP in their order");
                RiverSwitchFlipChecks.Has(st, @"if \(t is Pawn \|\| \(t\.def\.category == ThingCategory\.Building && !\(t is Blueprint\)\)\) \{ return false; \}", "pawns and buildings make the water wait (ruling 5)");
                RiverSwitchFlipChecks.Has(st, @"if \(!GenPlace\.TryPlaceThing\(item, dry, map, ThingPlaceMode\.Near, null, shore\)\) \{ GenSpawn\.Spawn\(item, c, map\); return false; \}",
                    "items wash to a dry shore; one that cannot be placed is put back and the square waits (never lost)");
                // the requeue order, modelled on a list exactly as Restore does it: pops 5,4,3 with 4 waiting -> stack [1,2,4]
                var stack = new System.Collections.Generic.List<int> { 1, 2, 3, 4, 5 };
                var waiting = new System.Collections.Generic.List<int>();
                for (int n = 0; n < 3; n++) { int c = stack[stack.Count - 1]; stack.RemoveAt(stack.Count - 1); if (c == 4) waiting.Add(c); }
                for (int i = waiting.Count - 1; i >= 0; i--) stack.Add(waiting[i]);
                Assert(string.Join(",", stack) == "1,2,4", "the waiting square is next in line: " + string.Join(",", stack));
            });

            Case("Pond_bed_predicate_is_kept_current", () =>
            {
                // POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 1 (GPT #9): one O(1) owner test for a dry pond square, set and
                // cleared at every place a square becomes or stops being dry bed, rebuilt from the bodies on load.
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"map\.terrainGrid\.SetTerrain\(c, dry\); bedGrid\[map\.cellIndices\.CellToIndex\(c\)\] = \(byte\)BedLevelsAt\(c\); return true;", "recession marks the bed");
                RiverSwitchFlipChecks.Has(ex, @"originalTerrain\.Remove\(i\); bedGrid\[i\] = 0; return RM_RestoreResult\.Restored;", "a verified restore clears it");
                RiverSwitchFlipChecks.Has(ex, @"detachedBedCells\[i\] = body\.id; bedGrid\[i\] = 0;", "a dug bed square is no longer bed");
                RiverSwitchFlipChecks.Has(ex, @"stock\.ReattachBedCell\(map, body, c, this\); bedGrid\[i\] = \(byte\)BedLevelsAt\(c\);", "a filled-in bed square is bed again");
                RiverSwitchFlipChecks.Has(ex, @"RebuildBedGrid\(\); ReportLostPaletteFluids\(\);", "rebuilt from the bodies in FinalizeInit");
                RiverSwitchFlipChecks.Has(ex, @"if \(c\.InBounds\(map\) && !IsExcavated\(c\)\) \{ bedGrid\[map\.cellIndices\.CellToIndex\(c\)\] = \(byte\)BedLevelsAt\(c\); \}", "the rebuild skips dug squares");
                RiverSwitchFlipChecks.Has(ex, @"return bedGrid\[i\] != 0 && depthGrid\[i\] == 0;", "a dug square is never bed");
                Assert(RM_Volume.BedLevels(false, 30) == 2 && RM_Volume.BedLevels(true, 300) == 4, "bed depths follow the water (ruling 3)");
            });

            Case("Pond_truncated_index_persists_and_ledger_probe_exists", () =>
            {
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"if \(owned\.truncated && !cellToBody\.ContainsKey\(fillFound\[f\]\)\) \{ owned\.cells\.Add\(map\.cellIndices\.IndexToCell\(fillFound\[f\]\)\); \}",
                    "a truncated body's newly walked cells are saved in its footprint (GPT #19)");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"public string LedgerReport\(\)", "the L0 ledger (G10)");
                RiverSwitchFlipChecks.Has(ex, @"fillGrid\[i\] -= 1; burnedLevelsTotal \+= 1f;", "burned levels are counted as an exit");
                string dbg = RiverSwitchFlipChecks.Src(Path.Combine("Debug", "FlowWorksDebugActions.cs"));
                RiverSwitchFlipChecks.Has(dbg, @"\[DebugAction\(CAT, ""Report water ledger \(L0\)""", "a dev action prints it");
            });
        }
    }
}
