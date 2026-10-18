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
                // a 10 shallow + 10 deep pond (60 levels); a deep bed square is dug out, then filled back in. POND_CAPACITY_FIX_DOUBLING_BED:
                // capacity = level unit x the beds in the footprint (RM_BedMath.CapacityForBeds), so it is exact in any order.
                float cap = 60f;
                float unit = RM_BedMath.LevelUnit(cap, 60);
                float less = RM_BedMath.CapacityForBeds(unit, 56);
                Assert(Math.Abs(less - 56f) < 1e-4, "a deep square takes its 4 levels with it: " + less);
                float back = RM_BedMath.CapacityForBeds(unit, 60);
                Assert(Math.Abs(back - cap) < 1e-4, "filled back in, the pond is its old size: " + back);
                // with a budget slider the share is proportional, still an exact inverse
                float scaled = 60f * 0.7f;
                float su = RM_BedMath.LevelUnit(scaled, 60);
                Assert(Math.Abs(RM_BedMath.CapacityForBeds(su, 58) + 2 * su - scaled) < 1e-4 && Math.Abs(RM_BedMath.CapacityForBeds(su, 60) - scaled) < 1e-4,
                    "the share is the square's part of whatever the pond was sized at");
                Assert(RM_BedMath.CapacityForBeds(unit, 0) == 0f && RM_BedMath.LevelUnit(cap, 0) == 0f, "degenerate inputs: no beds, no capacity, no unit");
                // review 2026-10-13: the LAST bed square of a pond dug out and filled back in must return the pond to its size; the
                // unit survives the empty footprint, so it does.
                float u4 = RM_BedMath.LevelUnit(4f, 4);
                Assert(RM_BedMath.CapacityForBeds(u4, 0) == 0f && Math.Abs(RM_BedMath.CapacityForBeds(u4, 4) - 4f) < 1e-4,
                    "the last bed square dug out and filled back in returns the pond to its size");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"next = \(byte\)first; RecordOriginalTerrain\(c\); DetachIfDryBed\(c, i\); \}",
                    "the first cut into a square checks for a dry bed (after the water record is kept)");
                RiverSwitchFlipChecks.Has(ex, @"if \(body == null \|\| !body\.receded\.Contains\(c\)\) \{ return; \}", "only a DRY (receded) bed square detaches");
                RiverSwitchFlipChecks.Has(ex, @"ClearFillTerrain\(c\); if \(!ReattachIfDetachedBed\(c, i\) && !ReturnUndetachedBedCut\(c, i\)\) \{ RestoreOriginalTerrain\(c\); \}",
                    "filling a detached bed to the surface returns it to its pond instead of writing unpaid water (G5)");
                RiverSwitchFlipChecks.Has(ex, @"map\.terrainGrid\.SetTerrain\(c, bed\); stock\.ReattachBedCell\(map, body, c, this\);", "it comes back as dry bed");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Collections\.Look\(ref detachedBedCells, ""RM_detachedBedCells""", "the natural-bed record survives a save (GPT #10)");
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"body\.cells\.Add\(c\); body\.receded\.Add\(c\);", "reattached as a receded square, so Restore re-wets it");
            });

            Case("Pond_restore_is_checked_and_waits_for_occupants", () =>
            {
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(map\.terrainGrid\.BaseTerrainAt\(c\) != original\) \{ return RM_RestoreResult\.WriteFailed; \} originalTerrain\.Remove\(i\); SetBed\(i, 0\); return RM_RestoreResult\.Restored;",
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
                RiverSwitchFlipChecks.Has(ex, @"map\.terrainGrid\.SetTerrain\(c, dry\); SetBed\(map\.cellIndices\.CellToIndex\(c\), BedLevelsAt\(c\)\); return true;", "recession marks the bed");
                RiverSwitchFlipChecks.Has(ex, @"originalTerrain\.Remove\(i\); SetBed\(i, 0\); return RM_RestoreResult\.Restored;", "a verified restore clears it");
                RiverSwitchFlipChecks.Has(ex, @"detachedBedCells\[i\] = body\.id; SetBed\(i, 0\);", "a dug bed square is no longer bed");
                RiverSwitchFlipChecks.Has(ex, @"stock\.ReattachBedCell\(map, body, c, this\); SetBed\(i, BedLevelsAt\(c\)\);", "a filled-in bed square is bed again");
                // step 2: SetBed is the ONE writer of the grid (count and climb generation follow every write)
                Assert(System.Text.RegularExpressions.Regex.Matches(ex, @"bedGrid\[[^\]]+\] = ").Count == 1, "bedGrid is written only inside SetBed");
                RiverSwitchFlipChecks.Has(ex, @"RebuildBedGrid\(\); ReportLostPaletteFluids\(\);", "rebuilt from the bodies in FinalizeInit");
                RiverSwitchFlipChecks.Has(ex, @"if \(c\.InBounds\(map\) && !IsExcavated\(c\)\) \{ SetBed\(map\.cellIndices\.CellToIndex\(c\), BedLevelsAt\(c\)\);", "the rebuild skips dug squares");
                RiverSwitchFlipChecks.Has(ex, @"return bedGrid\[i\] != 0 && depthGrid\[i\] == 0;", "a dug square is never bed");
                Assert(RM_Volume.BedLevels(false, 30) == 2 && RM_Volume.BedLevels(true, 300) == 4, "bed depths follow the water (ruling 3)");
            });

            Case("Pond_bed_hollow_math", () =>
            {
                // POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2 (Option B, rulings 2-4): the hollow depth, the lakebed per band,
                // and when a canal runs into a bed. PRODUCTION RM_Volume.
                Assert(RM_Volume.HollowDepth(0, 2, true) == 2 && RM_Volume.HollowDepth(0, 4, true) == 4, "a dry bed reads its depth (ruling 3)");
                Assert(RM_Volume.HollowDepth(0, 4, false) == 0, "hollows off: a dry bed is flat ground, as before");
                Assert(RM_Volume.HollowDepth(3, 4, true) == 3 && RM_Volume.HollowDepth(1, 0, false) == 1, "a dug square reads its dug depth whatever the bed");
                Assert(RM_Volume.HollowDepth(0, 0, true) == 0, "ground is ground");
                Assert(RM_Volume.LakebedFor(RM_Volume.ShallowBedLevels) == "RM_Lakebed_Shallow" && RM_Volume.LakebedFor(RM_Volume.LevelsPerSquare) == "RM_Lakebed_Deep",
                    "look (b): shallow bed 2, deep bed 4");
                Assert(RM_Volume.LakebedFor(RM_Volume.BedLevels(false, 30)) == "RM_Lakebed_Shallow" && RM_Volume.LakebedFor(RM_Volume.BedLevels(true, 300)) == "RM_Lakebed_Deep",
                    "the lakebed follows the water that was there");
                // §7 #8: water above the bed's floor runs in; at or below it, it stays
                Assert(RM_Volume.RunsIntoBed(1, 1, 2) && RM_Volume.RunsIntoBed(4, 4, 4) && RM_Volume.RunsIntoBed(2, 2, 2), "a brim-full canal always runs into a bed");
                Assert(RM_Volume.RunsIntoBed(4, 3, 2) && !RM_Volume.RunsIntoBed(4, 2, 2), "it runs until its surface is down at the bed's floor");
                Assert(!RM_Volume.RunsIntoBed(4, 0, 4) && !RM_Volume.RunsIntoBed(0, 0, 2) && !RM_Volume.RunsIntoBed(2, 2, 0), "a dry canal, no canal, no bed: nothing");
                // the drain stops where physics says: a D4 canal next to a D2 bed drains 4 -> 2 and stops (2 levels to the pond)
                int f = 4, moved = 0;
                while (RM_Volume.RunsIntoBed(4, f, 2)) { f--; moved++; }
                Assert(f == 2 && moved == 2, "D4 brim-full beside a 2-deep bed gives the pond 2 levels: f=" + f + " moved=" + moved);
            });

            Case("Pond_bed_hollow_round_trip_is_lifo_exact", () =>
            {
                // A1/A2 offline model: a pond of shallow rim (2) and deep middle (4) recedes outside-in; each dried square shows
                // its band's lakebed and reads its bed depth; refill pops last-in-first-out to the exact old water. The terrain
                // record is the production one (first record wins, restore removes it): modelled on lists, as Restore runs it.
                var water = new System.Collections.Generic.Dictionary<int, string> { { 0, "WaterShallow" }, { 1, "WaterShallow" }, { 2, "WaterDeep" }, { 3, "WaterDeep" }, { 4, "WaterShallow" } };
                var terrain = new System.Collections.Generic.Dictionary<int, string>(water);
                var record = new System.Collections.Generic.Dictionary<int, string>();
                var bed = new System.Collections.Generic.Dictionary<int, int>();
                var receded = new System.Collections.Generic.List<int>();
                foreach (int c in new[] { 0, 4, 1, 3, 2 })
                {
                    if (!record.ContainsKey(c)) record[c] = terrain[c];
                    int depth = RM_Volume.BedLevels(record[c] == "WaterDeep", record[c] == "WaterDeep" ? 300 : 30);
                    terrain[c] = RM_Volume.LakebedFor(depth);
                    bed[c] = depth;
                    receded.Add(c);
                }
                Assert(bed[0] == 2 && bed[1] == 2 && bed[4] == 2 && bed[2] == 4 && bed[3] == 4, "the hollow has the pond's shape: rim 2, middle 4");
                Assert(terrain[0] == "RM_Lakebed_Shallow" && terrain[2] == "RM_Lakebed_Deep", "and shows it");
                var order = new System.Collections.Generic.List<int>();
                while (receded.Count > 0)
                {
                    int c = receded[receded.Count - 1]; receded.RemoveAt(receded.Count - 1);
                    terrain[c] = record[c]; record.Remove(c); bed[c] = 0; order.Add(c);
                }
                Assert(string.Join(",", order) == "2,3,1,4,0", "re-wetted last-in-first-out: " + string.Join(",", order));
                foreach (var kv in water) Assert(terrain[kv.Key] == kv.Value, "square " + kv.Key + " came back as " + terrain[kv.Key]);
                Assert(record.Count == 0, "every record spent");
            });

            Case("Pond_bed_dig_starts_from_the_bed", () =>
            {
                // owner by card 2026-10-14: "When a colonist digs in a dried-out pond bed, what should happen? → Dig deeper from
                // the bed". PRODUCTION RM_Volume.FirstCutDepth; the Verse seams are pinned below.
                Assert(RM_Volume.FirstCutDepth(2, true, 4) == 3, "a dry shallow bed (2) is dug to 3, not restarted at 1");
                Assert(RM_Volume.FirstCutDepth(0, true, 4) == 1 && RM_Volume.FirstCutDepth(0, false, 4) == 1, "ground: 0 -> 1, as ever");
                Assert(RM_Volume.FirstCutDepth(2, false, 4) == 1, "hollows off: a bed is flat ground, the old 0 -> 1");
                Assert(RM_Volume.FirstCutDepth(4, true, 4) == -1, "a deep bed (4) is as deep as digging goes until DEEP_DIG (D 5) exists");
                Assert(RM_Volume.FirstCutDepth(4, true, 5) == 5, "can-fail: with a deeper max the deep bed goes 4 -> 5");
                Assert(RM_Volume.FirstCutDepth(2, true, 4, deepeningOn: false) == -1, "deepening off: a bed cut would deepen, refused");
                Assert(RM_Volume.FirstCutDepth(0, true, 4, deepeningOn: false) == 1, "deepening off still digs the first level of ground");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Assert(ex.Contains("int first = RM_Volume.FirstCutDepth(IsNaturalBed(c) ? bedGrid[i] : 0"), "Deepen's first cut reads the bed");
                Assert(RiverSwitchFlipChecks.Src("Designator_DigCanal.cs").Contains("eng.FirstCutDepthAt(c) < 0"), "the designator refuses a maxed bed");
                Assert(RiverSwitchFlipChecks.Src("WorkGiver_DigCanal.cs").Contains("FirstCutDepthAt(c) < 0"), "the work giver drops a stale bed designation");
                Assert(RiverSwitchFlipChecks.Src("JobDriver_DigCanal.cs").Contains("FirstCutDepthAt(c)"), "the dig work is the level below the bed");
                // review 2026-10-14: filling a bed cut back in ends AT the bed (2 -> 3 -> 2), never 3 -> 2 -> 1 -> 0 then a hollow of 2
                RiverSwitchFlipChecks.Has(ex, @"bool backToBed = bedFloor > 0 && newD <= bedFloor;", "fill-in stops at the bed's floor");
                RiverSwitchFlipChecks.Has(ex, @"long kept = RM_LevelPour\.KeptOnFillIn\(water, newD, newD == RM_ExcavationDepth\.Surface \|\| backToBed\);", "and displaces all the cell held");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                // review 2026-10-14: every route that flips it (control, section reset, confirmed Reset-all) re-pockets and redraws
                Assert(set.Contains("bool hollow = appliedHollow != pondBedHollowEnabled;") && set.Contains("appliedHollow = pondBedHollowEnabled;"),
                    "the hollow toggle is compared against its last-applied value, whatever changed it");
            });

            Case("Pond_bed_cut_review_2026_10_14", () =>
            {
                // (a) "Digging a dried bed takes the square out of its pond" OFF: the cut stays a receded square of its pond. It
                // used to keep its bed byte while dug (the load rebuild drops it: session and reload disagreed) and, filled back
                // in, got the recorded WATER written over it while on or off the refill stack (wet, unpaid, read as no hollow).
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(body == null \|\| !body\.receded\.Contains\(c\)\) \{ return; \} // [^\n]*?SetBed\(i, 0\); if \(!RimMandrakeFlowWorksSettings\.dugBedLeavesPondEnabled\) \{ return; \}",
                    "a dug bed square stops being bed whatever the setting; only the detach is gated");
                RiverSwitchFlipChecks.Has(ex, @"\|\| \(!detachedBedCells\.ContainsKey\(i\) && !IsUndetachedBedCut\(c\)\)\)",
                    "an undetached bed cut also fills back in to the bed's floor (hollows on)");
                RiverSwitchFlipChecks.Has(ex, @"private bool IsUndetachedBedCut\(IntVec3 c\) \{ return stock\.IndexedBodyAt\(map, c\) != null; \}",
                    "undetached = still in its pond's footprint (a refill drops a dug square from the receded list, not the footprint)");
                RiverSwitchFlipChecks.Has(ex, @"map\.terrainGrid\.SetTerrain\(c, bed\); if \(!body\.receded\.Contains\(c\)\) \{ body\.receded\.Add\(c\); // [^\n]*?\} SetBed\(i, BedLevelsAt\(c\)\); return true;",
                    "it comes back as dry bed with its bed depth, on the refill stack, the water record kept for Restore");
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(ex, @"private bool ReturnUndetachedBedCut\([^)]*\) \{[^}]*originalTerrain\.Remove"),
                    "the water record is not spent by the fill-in");
                // modelled: bed 2, cut to 3, filled once -> surface, bed 2 again (never 1 or 0)
                int bedFloor = 2, d = RM_Volume.FirstCutDepth(bedFloor, true, 4);
                int newD = d - 1;
                if (bedFloor > 0 && newD <= bedFloor) newD = 0;
                Assert(d == 3 && newD == 0 && RM_Volume.HollowDepth(newD, bedFloor, true) == 2, "one fill-in returns the 2-deep hollow: d=" + d + " newD=" + newD);
                // (b) backflow into a bed: a shut sluice on EITHER square stops it
                RiverSwitchFlipChecks.Has(ex, @"if \(f == 0 \|\| RM_FlowDoorRules\.SealsLiquid\(map\.edificeGrid\[c\]\)\) \{ continue; \}", "a sluice on the canal square holds the water in");
                RiverSwitchFlipChecks.Has(ex, @"RunsIntoBed\(depthGrid\[i\], f, NaturalBedDepthAt\(n\)\) && !RM_FlowDoorRules\.SealsLiquid\(map\.edificeGrid\[n\]\)\)",
                    "a sluice on the bed square keeps it out");
            });

            Case("Settings_section_reset_covers_int_fields", () =>
            {
                // review 2026-10-14: the shipped-default snapshot took bool and float fields only, so "Reset this section" on
                // Pits, ladders and shooting left pitRampMaxSpan (an int) where the player had put it.
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(set, @"if \(f\.FieldType == typeof\(bool\) \|\| f\.FieldType == typeof\(float\) \|\| f\.FieldType == typeof\(int\)\)",
                    "int settings are snapshotted for the section reset");
                RiverSwitchFlipChecks.Has(set, @"public static int pitRampMaxSpan = 3;", "the int setting the reset must reach");
                RiverSwitchFlipChecks.Has(set, @"""pitRampMaxSpan"", ""pitLadderSlowness""", "and it is listed in its section");
            });

            Case("Pond_bed_hollow_readers_pinned", () =>
            {
                // O2: every reader of a hole reads the dry bed; the writes lay the lakebed; the canal runs back into the pond.
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                // SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER: the seam still starts from the hollow; a dug swim square only lifts it to its
                // water surface (RM_SwimMath.ClimbDepthWithSwim, never deeper than the hollow)
                RiverSwitchFlipChecks.Has(ex, @"public int ClimbDepthAt\(IntVec3 c\) \{ int h = HollowDepthAt\(c\);", "the climb seam reads the hollow (PIT_POCKET's one seam)");
                RiverSwitchFlipChecks.Has(ex, @"RM_SwimMath\.ClimbDepthWithSwim\(h, s\) : h;", "and only a dug swim square reads its water surface");
                RiverSwitchFlipChecks.Has(ex, @"return RM_Volume\.HollowDepth\(depthGrid\[i\], bedGrid\[i\], RimMandrakeFlowWorksSettings\.pondBedHollowEnabled\);", "HollowDepthAt is the production math behind the setting");
                RiverSwitchFlipChecks.Has(ex, @"into\[i\] = \(byte\)RM_Volume\.HollowDepth\(depthGrid\[i\], bedGrid\[i\], true\);", "the pocket grid's input carries the beds");
                RiverSwitchFlipChecks.Has(ex, @"public int ClimbCellCount => excavatedCells\.Count \+ \(RimMandrakeFlowWorksSettings\.pondBedHollowEnabled \? bedCellCount : 0\);", "the early-out counts beds");
                RiverSwitchFlipChecks.Has(ex, @"return \(byte\)RM_Volume\.HollowDepth\(0, bedGrid\[i\], RimMandrakeFlowWorksSettings\.pondBedHollowEnabled\);", "DepthAt reads a dry bed (FillAt stays 0: an empty bed)");
                RiverSwitchFlipChecks.Has(ex, @"public bool CanLiquidEnter\(IntVec3 c\) \{ [^}]*return IsExcavated\(c\) \|\| IsNaturalLiquid\(c\); \}", "the legacy flood gate keeps its old meaning (no terrain writes on a bed)");
                RiverSwitchFlipChecks.Has(ex, @"if \(RimMandrakeFlowWorksSettings\.pondBedHollowEnabled\) \{ dry = LakebedTerrainFor\(c\); \} map\.terrainGrid\.SetTerrain\(c, dry\);", "recession lays the lakebed at the bed depth");
                RiverSwitchFlipChecks.Has(ex, @"if \(RimMandrakeFlowWorksSettings\.pondBedHollowEnabled\) \{ bed = LakebedTerrainFor\(c\);", "a filled-in detached bed comes back as lakebed");
                RiverSwitchFlipChecks.Has(ex, @"map\.terrainGrid\.TopTerrainAt\(c\) == mud && !pondMudSince\.ContainsKey\(map\.cellIndices\.CellToIndex\(c\)\)\) // POND_DEPTH: fresh mud keeps its time \{ map\.terrainGrid\.SetTerrain\(c, LakebedTerrainFor\(c\)\); \}", "an old save's bare mud bed is relaid as lakebed on load (POND_DEPTH: not fresh, timed mud)");
                RiverSwitchFlipChecks.Has(ex, @"sinkTransferredTotal \+= flowKernel\.sinkDrained; \} RunIntoBeds\(\);", "the canal-into-bed leg runs every pulse after the kernel");
                RiverSwitchFlipChecks.Has(ex, @"RM_Volume\.RunsIntoBed\(depthGrid\[i\], f, NaturalBedDepthAt\(n\)\)", "the leg uses the production rule");
                RiverSwitchFlipChecks.Has(ex, @"if \(!CanReturnLevels\(beds\[p\], fluid, 1\) \|\| !TakeLevelCore\(pours\[p\], out _\)\) \{ continue; \}", "checked before the take: nothing is lost (§7 #8: the stock is credited, never a dug cell)");
                RiverSwitchFlipChecks.Has(ex, @"if \(superdeepCellCount > 0 \|\| \(RM_PocketGrid\.Relative && ClimbCellCount > 0\)\)", "the fall detector runs over a drained pond");
                string trap = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_SuperdeepTrap.cs"));
                Assert(!trap.Contains("ExcavatedCellCount"), "no trap early-out ignores the beds");
                RiverSwitchFlipChecks.Has(trap, @"RM_PocketGrid\.Relative \? eng\.ClimbCellCount > 0 : eng\.SuperdeepCellCount > 0", "AnyHole sees a drained pond under the relative rule only (absolute: never a field of traps)");
                string path = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitPathing.cs"));
                RiverSwitchFlipChecks.Has(path, @"foreach \(IntVec3 c in eng\.ClimbCells\(\)\) \{ if \(IsTrapCell\(map, eng, c\)\)", "interim pathing walks the bed squares too");
                foreach (string f in new[] { "RM_PitDepthDraw.cs", "RM_PitLipOcclusion.cs", "RM_ExcavationWalls.cs", "RM_PitStepCost.cs" })
                {
                    string src = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", f));
                    // RM_PitStepCost reads ClimbDepthAt (the hollow, a dug swim square at its surface: SWIM_DUG_RESERVOIR_FIX)
                    string reader = f == "RM_PitStepCost.cs" ? ".ClimbDepthAt(" : ".HollowDepthAt(";
                    Assert(src.Contains(reader) && !src.Contains(".ExcavatedDepthAt("), f + ": reads the hollow depth, never the bare dug depth");
                }
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref pondBedHollowEnabled, ""pondBedHollowEnabled"", true\);", "the hollow is a saved Mod Setting, default on");
                RiverSwitchFlipChecks.Has(set, @"""dugBedLeavesPondEnabled"", ""pondBedHollowEnabled""", "and listed in its settings section");
            });

            Case("Pond_truncated_index_persists_and_ledger_probe_exists", () =>
            {
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"if \(owned\.truncated && !cellToBody\.ContainsKey\(fillFound\[f\]\)\) \{ IntVec3 far = map\.cellIndices\.IndexToCell\(fillFound\[f\]\); owned\.cells\.Add\(far\);",
                    "a truncated body's newly walked cells are saved in its footprint (GPT #19)");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"public string LedgerReport\(\)", "the L0 ledger (G10)");
                RiverSwitchFlipChecks.Has(ex, @"if \(!TakeLevelCore\(c, out FluidDef fluid\)\) \{ return false; \} burnedLevelsTotal \+= 1f;", "burned levels are counted as an exit");
                // review 2026-10-13: a pump's take is a MOVE into a tank, not a burn. Routed through BurnOffLevel it also bumped the
                // burned exit, so the L0 ledger read every pumped level twice (in the tank and as burned).
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(ex, @"public bool TryTakeLevel\([^)]*\) \{[^}]*BurnOffLevel"),
                    "TryTakeLevel must not count a pumped level as burned");
                RiverSwitchFlipChecks.Has(ex, @"public bool TryTakeLevel\(IntVec3 c, out FluidDef fluid\) \{ return TakeLevelCore\(c, out fluid\); \}", "a pump take moves the level without an exit");
                string dbg = RiverSwitchFlipChecks.Src(Path.Combine("Debug", "FlowWorksDebugActions.cs"));
                RiverSwitchFlipChecks.Has(dbg, @"\[DebugAction\(CAT, ""Report water ledger \(L0\)""", "a dev action prints it");
            });

            // Review day 2 (2026-10-17): under exact-level water the L0 ledger summed canals as whole notches (FillAt), so every
            // sheet's part-notch was missing and water crossing a notch boundary read as a leak; ponds were summed through the
            // float view; and the exact kernel's limitless input (LimitlessPaidDl) was counted but never printed.
            Case("Ledger_report_counts_decilitres_and_limitless_input", () =>
            {
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"canalsU \+= WaterDlAt\(c\) \* \(RM_Volume\.UnitsPerLevel / \(double\)RM_LevelSolve\.U\);", "can-fail: canals in decilitres, part-notch included");
                Assert(!ex.Contains("canalsU += FillAt(c)"), "can-fail: not whole notches");
                RiverSwitchFlipChecks.Has(ex, @"bodiesU \+= b\.stockDl \*", "ponds from the decilitre truth");
                Assert(ex.Contains("\" fromLimitless(session, exact)=\" + limitlessPaidDl"), "can-fail: the limitless input is disclosed");
            });

            // Review day 2: the settings screen still told the player the pre-R7 absolute rules (depth "held to 0-4" on load
            // though digs go to 20 m; "stopping power comes from superdeep cells and nothing else"; "three visible levels").
            Case("Settings_text_no_absolute_pit_rules", () =>
            {
                string m = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                foreach (string dead in new[] { "depth is held to 0-4", "stopping power comes from superdeep", "three visible levels", "drowning at D=4" })
                {
                    Assert(!m.Contains(dead), "can-fail: stale settings text: " + dead);
                }
            });

            // Review day 2: Refill wrote body.stock (the float view) every pulse; a big lake's decilitres went through a float and
            // back, so its books moved by the float's rounding each pulse. The float really does lose them:
            Case("Refill_stays_in_decilitres", () =>
            {
                long dl = 2_000_000_007L;   // a 200,000-notch lake, 7 dL over
                float view = (float)(dl / (double)RM_LevelSolve.U);
                Assert((long)Math.Round(view * (double)RM_LevelSolve.U) != dl, "control: the float view cannot hold this stock to the decilitre");
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                Assert(!st.Contains("body.stock = RM_StockMath.ClampToCapacity(body.stock, gained, body.capacity);"), "can-fail: no float round trip");
                RiverSwitchFlipChecks.Has(st, @"body\.stockDl = body\.stockDl \+ addDl > capDl \? capDl : body\.stockDl \+ addDl;", "refill adds whole dL, clamped at capacity");
            });
        }
    }
}
