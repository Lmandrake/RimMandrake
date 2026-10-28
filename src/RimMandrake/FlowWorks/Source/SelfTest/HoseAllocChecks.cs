// HOSE_LAY_FIX_GC_STORM_FROM_WORKER (live round 4, 2026-10-26: a relay wave on the 325 basin map ran 60 full GCs in 78 s on a
// 3.45 GB heap; Boehm stops the world and the pauses landed in DrawAll). The garbage one hose lay makes, measured offline on
// the live round's layout: two 4-notch basins (x 10..134 and x 190..314, z 2..321, banded so a hose stays on the gap), rigs
// in four columns (x 139/150/161/172, one per 5 rows) of two 2x2 reels and a pipe run, the Intake hose laid to A's lip and
// the Outflow hose to B's lip (up to 50 squares: maxLength 80, as the proof lays them).
//  A1 a lay on a worker's world copy allocates under 6 MB on average after warmup (GC.GetAllocatedBytesForCurrentThread
//     around 40 lays). Before the fix it was 340 MB (the clothoid solver's per-iteration arrays, LayOnce re-finishing every
//     lead-out pair, every Dubins arc sampled up front); a Boehm heap collects about once per third of its size allocated,
//     so on the live 3.45 GB heap a 200-lay wave went from about 60 collections to about one.
//     HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC (live round 7: lays at speed grew the heap ~40 MB/s, a full GC froze a frame
//     ~1.1 s): 4.7 MB -> 1.6 MB, bound 2.5 MB. Lead-out candidates keep their Dubins word, not a pose copy, and a pair's
//     finished poses come from a per-thread pool; the pair and Dubins-word rankings sort reused arrays (index-tiebroken,
//     the order LINQ OrderBy gave); RigHits samples into a reused set; the centre's join is found once per lay, not per
//     pair; the clothoid solve's per-node arrays are its thread's Scratch. 64 lays on this map hash identical before and
//     after. The rest is the lay's own output, the planner and Geo.Resample (shared with GSS).
//  A2 source: the levelling cycle walks a dug run once per cycle (an end in a run already walked takes its body for nothing)
//     and starts the next cycle at the first hose its walk budget turned away (HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP: every
//     end re-walked its 20000-square basin, so 60000 squares linked 2 rigs of 100).
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseAllocChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        internal const int Size = 325, LipA = 135, LipB = 189;
        internal static readonly int[] Columns = { 139, 150, 161, 172 };

        /// <summary>The live round's basin map as a hose sees it (RM_MapComponent_Hoses.World + RM_HoseBands.Apply).</summary>
        internal static CordWorld BasinWorld(out List<(int cx, int z)> rigs)
        {
            var w = new CordWorld(Size, Size);
            for (int z = 2; z <= 321; z++)
            {
                for (int x = 10; x <= 134; x++) { w.SetBand(new Cell(x, z), -4); w.SetExtraCost(new Cell(x, z), 3f); }
                for (int x = 190; x <= 314; x++) { w.SetBand(new Cell(x, z), -4); w.SetExtraCost(new Cell(x, z), 3f); }
            }
            rigs = new List<(int, int)>();
            for (int z = 4; z + 4 <= 321; z += 5)
                foreach (int cx in Columns)
                {
                    rigs.Add((cx, z));
                    for (int dz = 0; dz < 4; dz++)
                        for (int dx = 0; dx < 2; dx++) w.SetExtraCost(new Cell(cx + dx, z + dz), HoseMath.BuildingCrossCost);
                    for (int dz = 0; dz < 4; dz++) w.SetExtraCost(new Cell(cx + 2, z + dz), HoseMath.BuildingCrossCost);
                }
            return w;
        }

        internal static HoseLayInputs Inputs(int cx, int z, bool outflow)
        {
            var rect = new HoseReelRect(cx, outflow ? z + 2 : z, 2, 2);
            var sp = new HoseShapeParams { MaxLength = 80 };
            var end = outflow ? new Cell(LipB, z + 2) : new Cell(LipA, z);
            return new HoseLayInputs { Rect = rect, Start = rect.Mouth, End = end.Centre, Outward = rect.Outward, Shape = sp, Seed = (ulong)(cx * 1000 + z) };
        }

        /// <summary>Bytes per lay (this thread) over <paramref name="n"/> lays after <paramref name="warm"/> warmup lays.</summary>
        internal static double BytesPerLay(CordWorld copy, List<(int cx, int z)> rigs, int warm, int n, out int ok, out int gcs)
        {
            ok = 0;
            for (int i = 0; i < warm; i++) { var (cx, z) = rigs[i % rigs.Count]; HoseLayQueue.Compute(copy, Inputs(cx, z, i % 2 == 1)); }
            int g0 = GC.CollectionCount(0);
            long b0 = GC.GetAllocatedBytesForCurrentThread();
            for (int i = 0; i < n; i++)
            {
                var (cx, z) = rigs[(i * 7 + 3) % rigs.Count];
                HoseLay lay = HoseLayQueue.Compute(copy, Inputs(cx, z, i % 2 == 1));
                if (lay != null && lay.Ok) ok++;
            }
            long b1 = GC.GetAllocatedBytesForCurrentThread();
            gcs = GC.CollectionCount(0) - g0;
            return (b1 - b0) / (double)n;
        }

        private static ulong CellSigOf(CordWorld w, Cell c)
            => ((ulong)w.BlockAt(c) << 56) ^ ((w.IsDoor(c) ? 1UL : 0UL) << 55) ^ ((w.IsBusy(c) ? 1UL : 0UL) << 54)
               ^ ((ulong)(uint)w.BandAt(c) << 16) ^ ((ulong)w.LinkMask(c) << 8) ^ (ulong)BitConverter.SingleToInt32Bits(w.ExtraCost(c)) * 0x9E3779B97F4A7C15UL;

        public static void Run(Action<string, Action> Case)
        {
            Case("A1 a hose lay on the 325 basin map allocates under 2.5 MB after warmup", () =>
            {
                CordWorld w = BasinWorld(out var rigs);
                CordWorld copy = w.Clone();
                double per = BytesPerLay(copy, rigs, 8, 40, out int ok, out int gcs);
                Console.WriteLine($"    A1: {per / 1024.0:0.0} KB/lay over 40 lays ({ok} laid, gen0 GCs {gcs})");
                Assert(ok >= 30, $"the lays lay ({ok}/40): the layout is the live one");
                Assert(per < 2.5 * 1024 * 1024, $"{per / 1024.0:0.0} KB per lay (bound 2.5 MB; 4.7 MB before HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC, 340 MB before HOSE_LAY_FIX_GC_STORM_FROM_WORKER)");
                Assert(gcs <= 40, $"gen0 collections over 40 lays: {gcs}");
            });
            Case("A3 a recycled world (Reset + refill, CopyFrom) reads and lays exactly as a new one; the draw and recheck reuse", () =>
            {
                // HOSE_TICK_FIX_SPIKES_AT_SUPERFAST / HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC (live round 9): BuildWorld refills the
                // snapshot before last (CordWorld.Reset) and the lay pool refills stale copies (CordWorld.CopyFrom) instead of
                // allocating ~1.3 MB per rebuild or copy. A dirty world -- other bands, link, busy cells, blocks -- refilled
                // must give the fresh world's every cell signature and the same lays, byte for byte.
                CordWorld w = BasinWorld(out var rigs);
                CordWorld dirty = new CordWorld(Size, Size);
                for (int x = 0; x < Size; x += 3) { dirty.SetBand(new Cell(x, 7), 9); dirty.SetBlocked(new Cell(x, 9), BlockKind.Wall); dirty.SetBusy(new Cell(x, 11)); dirty.SetDoor(new Cell(x, 13)); dirty.SetExtraCost(new Cell(x, 15), 7f); }
                dirty.LinkBands(new Cell(5, 7), new Cell(5, 8));
                CordWorld copied = new CordWorld(Size, Size);
                copied.SetBand(new Cell(1, 1), 3); copied.SetBusy(new Cell(2, 2)); copied.LinkBands(new Cell(1, 1), new Cell(1, 2));
                copied.CopyFrom(w);
                // Reset then BasinWorld's own writes (what BuildWorld does) on the dirty world
                dirty.Reset();
                Assert(!dirty.HasBands && !dirty.HasBusy, "Reset leaves no band grid and no busy grid (HasBands / HasBusy as a new world)");
                for (int z = 2; z <= 321; z++)
                {
                    for (int x = 10; x <= 134; x++) { dirty.SetBand(new Cell(x, z), -4); dirty.SetExtraCost(new Cell(x, z), 3f); }
                    for (int x = 190; x <= 314; x++) { dirty.SetBand(new Cell(x, z), -4); dirty.SetExtraCost(new Cell(x, z), 3f); }
                }
                foreach (var (cx, z) in rigs)
                {
                    for (int dz = 0; dz < 4; dz++)
                        for (int dx = 0; dx < 2; dx++) dirty.SetExtraCost(new Cell(cx + dx, z + dz), HoseMath.BuildingCrossCost);
                    for (int dz = 0; dz < 4; dz++) dirty.SetExtraCost(new Cell(cx + 2, z + dz), HoseMath.BuildingCrossCost);
                }
                int diff = 0;
                for (int z = -1; z <= Size; z++)
                    for (int x = -1; x <= Size; x++)
                    {
                        var c = new Cell(x, z);
                        ulong sig = CellSigOf(w, c);
                        if (CellSigOf(dirty, c) != sig || CellSigOf(copied, c) != sig) diff++;
                    }
                Assert(diff == 0, $"{diff} cells read differently from a new world after Reset/CopyFrom");
                Assert(copied.HasBands == w.HasBands && copied.HasBusy == w.HasBusy, "CopyFrom copies the band/busy state");
                int laid = 0;
                for (int i = 0; i < 24; i++)
                {
                    var (cx, z) = rigs[(i * 11 + 5) % rigs.Count];
                    bool outflow = i % 2 == 1;
                    HoseLay a = HoseLayQueue.Compute(w.Clone(), Inputs(cx, z, outflow));
                    ulong fresh = HoseMateEndQueueChecks.LayHash(a);
                    Assert(HoseMateEndQueueChecks.LayHash(HoseLayQueue.Compute(dirty, Inputs(cx, z, outflow))) == fresh, $"lay {i}: a Reset world lays differently");
                    Assert(HoseMateEndQueueChecks.LayHash(HoseLayQueue.Compute(copied, Inputs(cx, z, outflow))) == fresh, $"lay {i}: a CopyFrom world lays differently");
                    if (a != null && a.Ok) laid++;
                }
                Assert(laid >= 18, $"the lays lay ({laid}/24): the check can fail");
                long b0 = GC.GetAllocatedBytesForCurrentThread();
                dirty.Reset();
                copied.CopyFrom(w);
                long bytes = GC.GetAllocatedBytesForCurrentThread() - b0;
                Assert(bytes < 4096, $"Reset + CopyFrom allocate {bytes} B (a new world is ~1.3 MB)");
                string comp = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(comp, @"cw\.Reset\(\);", "BuildWorld refills a retired snapshot");
                RiverSwitchFlipChecks.Has(comp, @"spareTick != now \|\| spareFrame != Time\.frameCount", "a snapshot retired in this same tick and frame is never refilled");
                RiverSwitchFlipChecks.Has(comp, @"w = layWorldsStale\.Pop\(\); w\.CopyFrom\(src\);", "the lay pool refills stale copies");
                RiverSwitchFlipChecks.Has(comp, @"CordWorld w = LegacyFrame \? World\(\) : World\(LayWorldMaxAge\);\s*if \(r\.trail\.Count > 0 && \(r\.lay == null \|\| !r\.TrailWalkable\(w\)\)\)", "TickRecheck reads the version-valid snapshot");
                RiverSwitchFlipChecks.Has(comp, @"List<Vector3> v = RibbonV; List<Vector2> uv = RibbonUv; List<int> tr = RibbonTr;", "Ribbon builds in scratch lists");
                Assert(!comp.Contains("all.AddRange(m.vertices)"), "the crossing shadow appends strips, no temporary mesh copied out");
            });
            Case("A2 source: a levelling cycle walks each dug run once and resumes at the hose its budget turned away", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_Levelling.cs"));
                // SELFTEST_A2_SOURCE_FIX_STALE_PATTERN: d802da77e8 moved the walk-once marks into RM_LevelRunScratch
                // (RM_LevelRunWalk.cs); the guard is the same rule, re-anchored there, and must still come before the budget
                RiverSwitchFlipChecks.Has(src, @"if \(run\.Reached\(startIdx\)\)\s*\{[^}]*index = run\.BodyOf\[startIdx\];", "an end in a run walked this cycle takes its body without walking");
                int reached = src.IndexOf("if (run.Reached(startIdx))", StringComparison.Ordinal), budget = src.IndexOf("if (walked >= WalkBudget ||", StringComparison.Ordinal);
                Assert(reached >= 0 && budget > reached, "a run walked this cycle is answered before the walk budget can turn its end away");
                RiverSwitchFlipChecks.Has(src, @"st\.run\.BeginCycle\(\);", "each cycle opens a new walk generation");
                string walk = RiverSwitchFlipChecks.Src("RM_LevelRunWalk.cs");
                RiverSwitchFlipChecks.Has(walk, @"public void BeginCycle\(\)\s*\{\s*CycleFirstWalk = WalkId \+ 1;\s*\}", "a new cycle forgets the last cycle's walks");
                RiverSwitchFlipChecks.Has(walk, @"public bool Reached\(int i\) => Mark\[i\] >= CycleFirstWalk;", "reached = marked by a walk of this cycle");
                RiverSwitchFlipChecks.Has(src, @"int hIndex = \(startAt \+ hi\) % hoses\.Count;", "the cycle starts at the cursor");
                RiverSwitchFlipChecks.Has(src, @"st\.hoseCursor = turnedAway < 0 \? 0 : turnedAway;", "the cursor is the first hose the budget turned away");
                var m = System.Text.RegularExpressions.Regex.Match(src, @"public const int WalkBudget = (\d+);");
                Assert(m.Success && int.Parse(m.Groups[1].Value) >= 2 * 125 * 320, "WalkBudget covers two 125 x 320 basins");
            });
        }
    }
}
