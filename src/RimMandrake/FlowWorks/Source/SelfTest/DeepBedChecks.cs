// POND_ELEVATION_BUILD_LAKES_RUN_DEEP (design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md §9; owner by card
// 2026-10-15, "Deeper ponds (lakes deeper than 4) ... Today? → Build it today"), plus the two pond-code fixes riding with it:
// POND_CAPACITY_FIX_DOUBLING_BED (C2-F1, C2-F7) and FILLIN_DISPLACE_FIX_DRY_POND_SNUB (C5-F8, C5-F9).
// The arithmetic is the PRODUCTION RM_BedMath / RM_RecessionSet / RM_PocketGridMath / RM_PitDrawMath / RM_WallFaceMath; the
// Verse-bound wiring (RM_LiquidStock, RM_MapComponent_Excavation, settings) is read from production source.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DeepBedChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A round lake on a w×h map: deep water inside radius rDeep, a shallow ring out to rAll.</summary>
        internal static (List<int> footprint, HashSet<int> deep) Lake(int w, int h, int cx, int cz, double rDeep, double rAll)
        {
            var fp = new List<int>();
            var deep = new HashSet<int>();
            for (int z = 0; z < h; z++)
            {
                for (int x = 0; x < w; x++)
                {
                    double r = Math.Sqrt((x - cx) * (x - cx) + (z - cz) * (z - cz));
                    if (r <= rAll)
                    {
                        int i = z * w + x;
                        fp.Add(i);
                        if (r <= rDeep) deep.Add(i);
                    }
                }
            }
            return (fp, deep);
        }

        /// <summary>The map's climb depth: the lake's beds, 0 on land.</summary>
        internal static byte[] Bowl(int w, int h, List<int> fp, int[] beds)
        {
            var d = new byte[w * h];
            for (int k = 0; k < fp.Count; k++) d[fp[k]] = (byte)beds[k];
            return d;
        }

        /// <summary>One pulse of RM_LiquidStock.Recede + Restore over the recession set (the same calls, in the same order),
        /// on a model map: wet[] is the terrain, receded the stack.</summary>
        internal static void Pulse(RM_RecessionSet rec, int w, int h, List<int> fp, Dictionary<int, int> bedOf, bool[] wet,
            List<int> receded, float stock, float unit, bool keepLast = true)
        {
            rec.Begin(w, h, fp, i => wet[i], i => bedOf[i], null);
            int supported = RM_BedMath.SupportedLevels(stock, unit);
            int guard = 0;
            while (RM_BedMath.ShouldShed(rec.WetLevels, rec.Count, supported, stock, keepLast) && guard++ < 1 << 20)
            {
                int pick = rec.Pick(true);
                if (pick < 0) break;
                wet[pick] = false;
                receded.Add(pick);
                rec.Remove(pick);
            }
            long wetLevels = rec.WetLevels;
            int wc = rec.Count;
            while (receded.Count > 0)
            {
                int c = receded[receded.Count - 1];
                int bed = bedOf[c];
                if (!RM_BedMath.CanRestore(wetLevels, wc, bed, supported, stock, keepLast)) break;
                receded.RemoveAt(receded.Count - 1);
                wet[c] = true;
                wc++;
                wetLevels += bed;
            }
            rec.Clear();
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("DeepBed_transform_is_a_gradual_bowl", () =>
            {
                int w = 120, h = 120;
                var (fp, deep) = Lake(w, h, 60, 60, 44, 48);
                int[] beds = new int[fp.Count];
                RM_BedMath.BedDepths(w, h, fp, i => deep.Contains(i), RM_BedMath.DefaultCellsPerLevel, RM_BedMath.DefaultMaxBedDepth, beds);
                int max = beds.Max();
                Assert(max > RM_Volume.LevelsPerSquare, "a 88-wide deep lake runs deeper than 4 in the middle: " + max);
                Assert(max <= RM_BedMath.DefaultMaxBedDepth, "capped at the max bed: " + max);
                int centre = fp.IndexOf(60 * w + 60);
                Assert(beds[centre] == max, "the deepest square is the middle: " + beds[centre] + " vs " + max);
                for (int k = 0; k < fp.Count; k++)
                {
                    if (!deep.Contains(fp[k])) Assert(beds[k] == RM_Volume.ShallowBedLevels, "shallow water is a 2 bed (ruling 3)");
                    else Assert(beds[k] >= RM_Volume.LevelsPerSquare, "deep water is at least the deep notch (owner: 'at least 4 notches')");
                }
                // §9.4: 4 + floor((d - 3) / 4): d = 1..6 → 4, d = 7 → 5, d = 11 → 6
                Assert(RM_BedMath.DeepBedLevels(1, 4, 20) == 4 && RM_BedMath.DeepBedLevels(6, 4, 20) == 4 && RM_BedMath.DeepBedLevels(7, 4, 20) == 5
                    && RM_BedMath.DeepBedLevels(11, 4, 20) == 6, "the design's slope (d0 3, s 4)");
                Assert(RM_BedMath.DeepBedLevels(1000, 1, 20) == 20 && RM_BedMath.DeepBedLevels(1000, 1, 999) == RM_BedMath.MaxStorableDepth,
                    "capped by the setting, and by the byte the record keeps");
                Assert(RM_BedMath.DeepBedLevels(1000, 4, 2) == RM_Volume.LevelsPerSquare, "a cap below the notch still leaves deep water 4");
                // gradual: every N/S/E/W step on the map (lake and land) is at most the deep notch, and inside the deep water at
                // most one level -- so the pocket grid's "K >= MaxDepth climbs every step" shortcut stays true, and the person
                // band sees no pocket at all (owner ruling 4).
                byte[] map = Bowl(w, h, fp, beds);
                int worstInside = 0, worstAny = 0;
                for (int z = 0; z < h; z++)
                {
                    for (int x = 0; x + 1 < w; x++)
                    {
                        int a = z * w + x;
                        foreach (int b in new[] { a + 1, z + 1 < h ? a + w : -1 })
                        {
                            if (b < 0) continue;
                            int s = Math.Abs(map[a] - map[b]);
                            worstAny = Math.Max(worstAny, s);
                            if (deep.Contains(a) && deep.Contains(b)) worstInside = Math.Max(worstInside, s);
                        }
                    }
                }
                Assert(worstInside <= 1, "inside the deep water neighbours differ by one level at most: " + worstInside);
                Assert(worstAny <= RM_Volume.LevelsPerSquare, "nowhere a step past the deep notch: " + worstAny);
                for (int k = 1; k < RM_ExcavationDepth_MaxDepth(); k++)
                {
                    var lab = RM_PocketGridMath.Label(map, w, h, k);
                    int pockets = 0;
                    for (int i = 0; i < w * h; i++) if (lab.IsPocketCell(i)) pockets++;
                    if (k >= 2) Assert(pockets == 0, "band K " + k + ": a drained " + max + "-deep bowl holds nobody, got " + pockets + " pocket squares");
                }
                // the same depth as a SHEER hole would trap a person: the gradual shape is what frees them
                var sheer = new byte[w * h];
                foreach (int i in fp) sheer[i] = (byte)max;
                var ls = RM_PocketGridMath.Label(sheer, w, h, 2);
                Assert(ls.IsPocketCell(60 * w + 60), "the control: a sheer " + max + "-deep hole is a pocket for a person");
                // slope setting: steeper (1 square a level) reaches the cap sooner, still ≤ 1 per cardinal step inside
                int[] steep = new int[fp.Count];
                RM_BedMath.BedDepths(w, h, fp, i => deep.Contains(i), 1, 12, steep);
                Assert(steep.Max() == 12, "slope 1 hits the 12 cap: " + steep.Max());
            });

            Case("DeepBed_small_ponds_unchanged", () =>
            {
                // a 9x9 deep pond: every square is within 4 of the shore, so no bed passes 4 and nothing is recorded
                int w = 30, h = 30;
                var fp = new List<int>(); var deep = new HashSet<int>();
                for (int z = 10; z < 19; z++) for (int x = 10; x < 19; x++) { fp.Add(z * w + x); deep.Add(z * w + x); }
                int[] beds = new int[fp.Count];
                RM_BedMath.BedDepths(w, h, fp, i => deep.Contains(i), RM_BedMath.DefaultCellsPerLevel, RM_BedMath.DefaultMaxBedDepth, beds);
                Assert(beds.All(b => b == RM_Volume.LevelsPerSquare), "a pond under 13 squares across keeps the old 4 everywhere");
                // edge squares count as shore
                var e = new List<int> { 0, 1, w, w + 1 };
                int[] eb = new int[4];
                RM_BedMath.BedDepths(w, h, e, i => true, 1, 20, eb);
                Assert(eb.All(b => b == 4), "out of the map is shore");
            });

            Case("DeepBed_drawdown_sheds_shallowest_first_and_refills_lifo_exact", () =>
            {
                int w = 70, h = 70;
                var (fp, deep) = Lake(w, h, 35, 35, 26, 29);
                int[] beds = new int[fp.Count];
                RM_BedMath.BedDepths(w, h, fp, i => deep.Contains(i), 2, 20, beds);
                var bedOf = new Dictionary<int, int>();
                long total = 0;
                for (int k = 0; k < fp.Count; k++) { bedOf[fp[k]] = beds[k]; total += beds[k]; }
                float unit = 0.7f;                       // a budget slider off 1: one level = 0.7 fill-units
                float cap = RM_BedMath.CapacityForBeds(unit, (int)total);
                Assert(Math.Abs(RM_BedMath.LevelUnit(cap, (int)total) - unit) < 1e-5, "the level unit reads back");
                var wet = new bool[w * h];
                foreach (int i in fp) wet[i] = true;
                var receded = new List<int>();
                var rec = new RM_RecessionSet();
                var snapshots = new List<string>();
                // pump out 3% of the capacity per pulse until dry, then back in the same steps
                int steps = 34;
                float[] stocks = new float[steps + 1];
                for (int s = 0; s <= steps; s++) stocks[s] = Math.Max(0f, cap * (1f - s / (float)steps * 1.02f));
                for (int s = 0; s <= steps; s++)
                {
                    float stock = stocks[s];
                    Pulse(rec, w, h, fp, bedOf, wet, receded, stock, unit);
                    long wl = 0; int wc = 0; int minWet = int.MaxValue, maxDry = 0;
                    foreach (int i in fp)
                    {
                        if (wet[i]) { wl += bedOf[i]; wc++; minWet = Math.Min(minWet, bedOf[i]); }
                        else maxDry = Math.Max(maxDry, bedOf[i]);
                    }
                    int sup = RM_BedMath.SupportedLevels(stock, unit);
                    Assert(wl <= sup || wc <= 1, "pulse " + s + ": the wet beds never hold more than the stock (" + wl + " > " + sup + ")");
                    Assert(wc == 0 || maxDry <= minWet, "pulse " + s + ": the drawdown dries the shallow beds first (dry " + maxDry + " > wet " + minWet + ")");
                    snapshots.Add(string.Join(",", receded));
                }
                Assert(receded.Count >= fp.Count - 1, "drained to its last square (keep-last): " + receded.Count + " of " + fp.Count);
                for (int s = steps; s >= 0; s--)
                {
                    float stock = stocks[s];
                    Pulse(rec, w, h, fp, bedOf, wet, receded, stock, unit);
                    // on the way back each stock level shows the SAME wet set it showed on the way down (LIFO, exact)
                    Assert(string.Join(",", receded) == snapshots[s], "refill step " + s + " re-wets to the exact drain-time shape");
                }
                Assert(receded.Count == 0 && fp.All(i => wet[i]), "full again: every square wet, the stack empty");
            });

            Case("DeepBed_equal_beds_match_the_old_average_model", () =>
            {
                // every bed equal (one weight a square, as with deepBedsEnabled off or a small pond): the level count gives the
                // old floor(stock / perCell) with keep-last, at every stock
                var rnd = new Random(7);
                for (int t = 0; t < 400; t++)
                {
                    int cells = 1 + rnd.Next(60);
                    int bed = rnd.Next(2) == 0 ? 2 : 4;
                    float cap = cells * bed * (0.2f + (float)rnd.NextDouble() * 3f);
                    float stock = (float)rnd.NextDouble() * cap * 1.1f;
                    float perCell = cap / cells;
                    int oldSupported = RM_StockMath.SupportedCellsKeepingLast(stock, perCell, true);
                    int sup = RM_BedMath.SupportedLevels(stock, cap / (cells * bed));
                    int wetNew = cells;
                    while (RM_BedMath.ShouldShed((long)wetNew * bed, wetNew, sup, stock, true)) wetNew--;
                    int boundary = (int)Math.Floor(stock / perCell);
                    bool nearBoundary = Math.Abs(stock / perCell - Math.Round(stock / perCell)) < 1e-3;
                    Assert(nearBoundary || Math.Min(oldSupported, cells) == wetNew,
                        "t" + t + ": old " + oldSupported + " new " + wetNew + " (cells " + cells + " bed " + bed + " stock " + stock + " cap " + cap + ")");
                    _ = boundary;
                }
            });

            Case("DeepBed_recession_set_matches_the_old_order", () =>
            {
                // equal beds: the order is the old outside-in order (fewest neighbours, furthest from the centroid, lowest
                // index), checked against a direct port of the retired dictionary walk on a ragged pond
                int w = 25, h = 25;
                var rnd = new Random(3);
                var fp = new List<int>();
                for (int z = 4; z < 20; z++) for (int x = 3; x < 22; x++) if (rnd.NextDouble() < 0.85) fp.Add(z * w + x);
                var bedOf = fp.ToDictionary(i => i, i => 4);
                var wet = new bool[w * h];
                foreach (int i in fp) wet[i] = true;
                var rec = new RM_RecessionSet();
                rec.Begin(w, h, fp, i => wet[i], i => bedOf[i], null);
                var live = new HashSet<int>(fp);
                long sx = 0, sz = 0;
                foreach (int i in fp) { sx += i % w; sz += i / w; }
                int cx = (int)(sx / fp.Count), cz = (int)(sz / fp.Count);
                int n8(int c) { int x = c % w, z = c / w, k = 0; for (int dz = -1; dz <= 1; dz++) for (int dx = -1; dx <= 1; dx++) if ((dx != 0 || dz != 0) && x + dx >= 0 && x + dx < w && z + dz >= 0 && z + dz < h && live.Contains((z + dz) * w + x + dx)) k++; return k; }
                int[] rx = { 0, 1, 1, 1, 0, -1, -1, -1 }, rz = { 1, 1, 0, -1, -1, -1, 0, 1 };
                int ring(int c) { int x = c % w, z = c / w, m = 0; for (int k = 0; k < 8; k++) { int X = x + rx[k], Z = z + rz[k]; if (X >= 0 && Z >= 0 && X < w && Z < h && live.Contains(Z * w + X)) m |= 1 << k; } return m; }
                for (int step = 0; step < 40; step++)
                {
                    int best = -1, bn = int.MaxValue, bd = -1, bi = int.MaxValue;
                    foreach (int c in live)
                    {
                        int x = c % w, z = c / w, d = (x - cx) * (x - cx) + (z - cz) * (z - cz), nn = n8(c);
                        if (!RM_StockMath.PrefersCandidate(nn, d, c, bn, bd, bi)) continue;
                        if (!RM_StockMath.LocalRemovalKeepsConnected(ring(c))) continue;
                        best = c; bn = nn; bd = d; bi = c;
                    }
                    if (best < 0) break;
                    int got = rec.Pick(true);
                    Assert(got == best, "step " + step + ": the set picks " + got + ", the old walk " + best);
                    rec.Remove(got);
                    live.Remove(got);
                }
            });

            Case("DeepBed_readers_read_past_four", () =>
            {
                Assert(RM_Volume.HollowDepth(0, 12, true) == 12 && RM_Volume.HollowDepth(0, 12, false) == 0, "a dry 12 bed reads 12 (hollows on), flat off");
                Assert(RM_Volume.LakebedFor(12) == "RM_Lakebed_Abyss" && RM_Volume.LakebedFor(RM_Volume.AbyssBedLevels - 1) == "RM_Lakebed_Deep"
                    && RM_Volume.LakebedFor(RM_Volume.LevelsPerSquare) == "RM_Lakebed_Deep" && RM_Volume.LakebedFor(2) == "RM_Lakebed_Shallow",
                    "terrain bands: shallow < 4 <= deep < 8 <= abyss");
                // §9.5: the pawn sink is capped at the deep notch (no sprite drawn cells south of its square)
                Assert(Math.Abs(RM_PitDrawMath.SinkFor(12, 0.3f) - RM_PitDrawMath.SinkFor(4, 0.3f)) < 1e-6, "the sink stops at 4 levels");
                Assert(RM_PitTrapMath.FallDropScale(12, 4) == 1f, "a long drop is the full fall, never more");
                Assert(RM_WallFaceMath.NorthFaceHeight(12) == RM_WallFaceMath.NorthMax && RM_WallFaceMath.SouthLining(12) > 0f, "wall faces clamp past 4");
                // a 12-deep square can never be dug from (the kernel never sees a depth past MaxDepth), and a canal beside it
                // runs into it by water height (head), the only flow seam a bed has
                Assert(RM_Volume.FirstCutDepth(12, true, 4) == -1, "digging from a bed deeper than a dig goes is refused");
                Assert(RM_Volume.RunsIntoBed(4, 1, 12) && RM_Volume.RunsIntoBed(1, 1, 5) && !RM_Volume.RunsIntoBed(4, 4, 0), "a canal's water above a deep bed's floor runs in");
                string dep = RiverSwitchFlipChecks.Src("RM_ExcavationDepth.cs");
                RiverSwitchFlipChecks.Has(dep, @"default: return depth > Superdeep \? RimMandrakeFlowWorks_DefOf\.RM_Channel_Superdeep : null;", "a climb in a deep bowl is priced, not free");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"byte recorded = bedRecord\[map\.cellIndices\.CellToIndex\(c\)\]; if \(recorded != 0\) \{ return recorded;", "BedLevelsAt reads the record first");
                RiverSwitchFlipChecks.Has(ex, @"DataExposeUtility\.LookByteArray\(ref bedRecord, ""RM_bedDepthRecord""\);", "the record is saved with the map");
                RiverSwitchFlipChecks.Has(ex, @"case ""RM_Lakebed_Abyss"": return RimMandrakeFlowWorks_DefOf\.RM_Lakebed_Abyss;", "the abyss bed is laid");
                Assert(File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_Volume.cs")), "..", "Defs", "Canals", "TerrainDefs", "FlowWorks_Terrain.xml"))
                    .Contains("<defName>RM_Lakebed_Abyss</defName>"), "the abyss TerrainDef ships");
            });

            Case("DeepBed_wiring_and_settings", () =>
            {
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                RiverSwitchFlipChecks.Has(st, @"if \(!body\.limitless && RimMandrakeFlowWorksSettings\.deepBedsEnabled\) \{ RecordDeepBeds\(map, fillFound, owner\); \}", "deep beds recorded at formation, limited lakes only");
                Assert(st.IndexOf("RecordDeepBeds(map, fillFound, owner)") < st.IndexOf("body.capacity = CapacityOf(body, owner);"), "recorded before the capacity is summed");
                RiverSwitchFlipChecks.Has(st, @"if \(ownedId < 0 && truncated && !touchesEdge && lakeCap > MaxBodyCells\)", "the ocean cap re-walks an inland lake");
                RiverSwitchFlipChecks.Has(st, @"if \(lakeOwned < 0 && !lakeEdge && !lakeTruncated\)", "only a complete inland body is kept as a lake");
                RiverSwitchFlipChecks.Has(st, @"if \(body\.receded\.Count == 0 && body\.stock >= body\.capacity && \(!depth \|\| !body\.depthStaged\)\) \{ continue; \}", "a full untouched lake costs no scan per pulse (POND_DEPTH: once laid back to its own water)");
                RiverSwitchFlipChecks.Has(st, @"beds \? \(Func<int, int>\)\(i => owner\.BedLevelsAt\(map\.cellIndices\.IndexToCell\(i\)\)\) : \(i => 1\)", "off: one weight a square (the old model)");
                string body = RiverSwitchFlipChecks.Src("RM_LiquidBody.cs");
                RiverSwitchFlipChecks.Has(body, @"Scribe_Values\.Look\(ref levelUnit, ""levelUnit"", 0f\);", "the level unit is saved");
                RiverSwitchFlipChecks.Has(body, @"if \(Scribe\.mode == LoadSaveMode\.Saving && cells != null && cells\.Count > PackFootprintOver\)", "a big footprint saves packed");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                foreach (string f in new[] { @"deepBedsEnabled, ""deepBedsEnabled"", true", @"deepBedMaxDepth, ""deepBedMaxDepth"", 20f", @"deepBedCellsPerLevel, ""deepBedCellsPerLevel"", 4f", @"drainableLakeMaxCells, ""drainableLakeMaxCells"", 40000f" })
                    RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref " + f + @"\);", "saved Mod Setting " + f);
                RiverSwitchFlipChecks.Has(set, @"""pondBedHollowEnabled"", ""deepBedsEnabled"", ""deepBedMaxDepth"", ""deepBedCellsPerLevel"", ""drainableLakeMaxCells""", "listed in its settings section");
                RiverSwitchFlipChecks.Has(set, @"\.Declare\(""deepBedsEnabled"", ""deepBedMaxDepth"", ""deepBedCellsPerLevel""\)", "the sliders grey with their switch");
                // footprint packing round-trips in order (the recession stack's order is the refill order)
                var xs = new[] { 0, 1, 249, 300, 65535 }; var zs = new[] { 5, 0, 248, 1, 2 };
                byte[] p = RM_BedMath.PackXZ(xs.Length, k => xs[k], k => zs[k]);
                Assert(RM_BedMath.PackedCount(p) == 5 && Enumerable.Range(0, 5).All(k => RM_BedMath.PackedX(p, k) == xs[k] && RM_BedMath.PackedZ(p, k) == zs[k]),
                    "pack/unpack keeps every square and its order");
                Assert(RM_BedMath.PackedCount(null) == 0 && RM_BedMath.PackXZ(0, k => 0, k => 0).Length == 0, "an empty stack packs to nothing");
            });

            Case("Pond_capacity_dug_out_and_back_in_any_order", () =>
            {
                // POND_CAPACITY_FIX_DOUBLING_BED (C2-F1, GPT hand-verified): beds 2 + 4, capacity 6. Dig out 2, dig out 4, fill
                // back 2, fill back 4. The ratio math read 6 -> 4 -> 4 (last square kept the capacity) -> 4 (sum 0, no scale)
                // -> 12. Capacity is now the level unit times the beds present.
                float unit = RM_BedMath.LevelUnit(6f, 6);
                float c1 = RM_BedMath.CapacityForBeds(unit, 4);      // 2 dug out
                float c2 = RM_BedMath.CapacityForBeds(unit, 0);      // 4 dug out: nothing left
                float c3 = RM_BedMath.CapacityForBeds(unit, 2);      // 2 back
                float c4 = RM_BedMath.CapacityForBeds(unit, 6);      // 4 back
                Assert(Math.Abs(c1 - 4f) < 1e-5 && c2 == 0f && Math.Abs(c3 - 2f) < 1e-5 && Math.Abs(c4 - 6f) < 1e-5,
                    "6 -> 4 -> 0 -> 2 -> 6, got " + c1 + " " + c2 + " " + c3 + " " + c4);
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                Assert(!Regex.IsMatch(st, @"CapacityWithoutBed|CapacityWithBed"), "the ratio pair is gone from the stock model");
                Assert(Regex.Matches(st, @"body\.capacity = RM_BedMath\.CapacityForBeds\(unit, BedSum\(body, owner\)\);").Count == 2,
                    "detach and reattach both size the pond by unit x beds");
                RiverSwitchFlipChecks.Has(st, @"body\.levelUnit = RM_BedMath\.LevelUnit\(body\.capacity, BedSum\(body, owner\)\);", "the unit is fixed at formation");
                // C2-F7: sticky-limitless off, a truncated LIMITED body's far squares bring their own capacity and water
                RiverSwitchFlipChecks.Has(st, @"if \(!owned\.limitless\) \{ float add = LevelUnitOf\(owned, owner\) \* owner\.BedLevelsAt\(far\); owned\.capacity \+= add; owned\.stock \+= add; \}",
                    "a limited body never grows squares without capacity");
            });

            Case("Fillin_displacement_reaches_a_dry_pond_and_the_whole_network", () =>
            {
                // FILLIN_DISPLACE_FIX_DRY_POND_SNUB: C5-F8 the walk offered only WET pond squares, so a fully drained pond beside
                // a filled-in canal took nothing and the liquid was destroyed; C5-F9 the walk stopped at 6000 squares.
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(IsSourceCell\(c\) \|\| IsDisplaceBed\(c\)\) \{ sources\.Add\(c\); continue; \}", "a dry bed square is a destination");
                RiverSwitchFlipChecks.Has(ex, @"if \(\(IsExcavated\(n\) \|\| IsSourceCell\(n\) \|\| IsDisplaceBed\(n\)\) && !RM_FlowDoorRules\.SealsLiquid", "and the walk reaches it");
                RiverSwitchFlipChecks.Has(ex, @"private bool IsDisplaceBed\(IntVec3 c\) \{ return RimMandrakeFlowWorksSettings\.pondReturnLegEnabled && IsNaturalBed\(c\); \}", "gated by the return leg's switch");
                RiverSwitchFlipChecks.Has(ex, @"int walkCap = map\.cellIndices\.NumGridCells; while \(queue\.Count > 0 && remaining > 0 && walked < walkCap\)", "the walk is bounded by the map, not 6000");
                Assert(!Regex.IsMatch(ex, @"walked < MaxComponentCells"), "the 6000 cap no longer stops the displacement walk");
            });

            Case("DeepBed_bench_offline", () =>
            {
                // Per-tick cost: nothing here runs per tick (pillar 2: per pulse, default every 250 ticks). Formation runs once per
                // lake. MEASURED here on the selftest host; the numbers are printed for the item note.
                int w = 250, h = 250;
                var (fp, deep) = Lake(w, h, 125, 125, 108, 112);   // ~39k squares, the default drainable cap's size
                var sw = Stopwatch.StartNew();
                var found = new List<int>(); var q = new List<int>(); var seen = new HashSet<int>();
                var fpSet = new HashSet<int>(fp);
                RM_FlowKernel.CollectBody(w, h, 125 * w + 125, i => fpSet.Contains(i), i => -1, 62500, found, q, seen, out bool edge, out bool trunc);
                double walkMs = sw.Elapsed.TotalMilliseconds;
                Assert(found.Count == fp.Count && !edge && !trunc, "the lake walk finds the whole inland lake: " + found.Count + "/" + fp.Count);
                sw.Restart();
                int[] beds = new int[fp.Count];
                RM_BedMath.BedDepths(w, h, fp, i => deep.Contains(i), 4, 20, beds);
                double bedMs = sw.Elapsed.TotalMilliseconds;
                var bedOf = new Dictionary<int, int>(); long total = 0;
                for (int k = 0; k < fp.Count; k++) { bedOf[fp[k]] = beds[k]; total += beds[k]; }
                var wet = new bool[w * h]; foreach (int i in fp) wet[i] = true;
                var rec = new RM_RecessionSet();
                rec.Begin(w, h, fp, i => wet[i], i => bedOf[i], null);   // warm the arrays
                rec.Clear();
                sw.Restart();
                rec.Begin(w, h, fp, i => wet[i], i => bedOf[i], null);
                double beginMs = sw.Elapsed.TotalMilliseconds;
                sw.Restart();
                for (int k = 0; k < 64; k++) { int p = rec.Pick(true); if (p < 0) break; rec.Remove(p); }
                double pick64Ms = sw.Elapsed.TotalMilliseconds;
                rec.Clear();
                Console.WriteLine("  DeepBed bench: lake " + fp.Count + " squares, deepest " + beds.Max() + ", capacity " + total + " levels; walk "
                    + walkMs.ToString("F1") + " ms, beds " + bedMs.ToString("F1") + " ms (both once per lake); per drain pulse: scan "
                    + beginMs.ToString("F2") + " ms + 64 sheds " + pick64Ms.ToString("F2") + " ms");
                Assert(walkMs + bedMs < 2000 && beginMs + pick64Ms < 500, "generous ceilings so a loaded host does not flake");
            });
        }

        private static int RM_ExcavationDepth_MaxDepth() => 4;   // RM_ExcavationDepth is Verse-bound; its MaxDepth (Superdeep) is 4
    }
}
