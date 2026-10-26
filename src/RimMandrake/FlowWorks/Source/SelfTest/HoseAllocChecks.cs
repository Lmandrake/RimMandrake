// HOSE_LAY_FIX_GC_STORM_FROM_WORKER (live round 4, 2026-10-26: a relay wave on the 325 basin map ran 60 full GCs in 78 s on a
// 3.45 GB heap; Boehm stops the world and the pauses landed in DrawAll). The garbage one hose lay makes, measured offline on
// the live round's layout: two 4-notch basins (x 10..134 and x 190..314, z 2..321, banded so a hose stays on the gap), rigs
// in four columns (x 139/150/161/172, one per 5 rows) of two 2x2 reels and a pipe run, the Intake hose laid to A's lip and
// the Outflow hose to B's lip (up to 50 squares: maxLength 80, as the proof lays them).
//  A1 a lay on a worker's world copy allocates under 6 MB on average after warmup (GC.GetAllocatedBytesForCurrentThread
//     around 40 lays). Before the fix it was 340 MB (the clothoid solver's per-iteration arrays, LayOnce re-finishing every
//     lead-out pair, every Dubins arc sampled up front); a Boehm heap collects about once per third of its size allocated,
//     so on the live 3.45 GB heap a 200-lay wave went from about 60 collections to about one. The rest is the lay's own
//     output and the per-fit point lists: further cuts buy nothing a player sees.
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

        public static void Run(Action<string, Action> Case)
        {
            Case("A1 a hose lay on the 325 basin map allocates under 6 MB after warmup", () =>
            {
                CordWorld w = BasinWorld(out var rigs);
                CordWorld copy = w.Clone();
                double per = BytesPerLay(copy, rigs, 8, 40, out int ok, out int gcs);
                Console.WriteLine($"    A1: {per / 1024.0:0.0} KB/lay over 40 lays ({ok} laid, gen0 GCs {gcs})");
                Assert(ok >= 30, $"the lays lay ({ok}/40): the layout is the live one");
                Assert(per < 6 * 1024 * 1024, $"{per / 1024.0:0.0} KB per lay (bound 6 MB; 340 MB before the fix)");
                Assert(gcs <= 40, $"gen0 collections over 40 lays: {gcs}");
            });
            Case("A2 source: a levelling cycle walks each dug run once and resumes at the hose its budget turned away", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_Levelling.cs"));
                RiverSwitchFlipChecks.Has(src, @"if \(st\.mark\[startIdx\] >= st\.cycleFirstWalk\)\s*\{[^}]*index = st\.bodyOf\[startIdx\];", "an end in a run walked this cycle takes its body without walking");
                RiverSwitchFlipChecks.Has(src, @"st\.cycleFirstWalk = st\.walkId \+ 1;", "a new cycle forgets the last cycle's walks");
                RiverSwitchFlipChecks.Has(src, @"int hIndex = \(startAt \+ hi\) % hoses\.Count;", "the cycle starts at the cursor");
                RiverSwitchFlipChecks.Has(src, @"st\.hoseCursor = turnedAway < 0 \? 0 : turnedAway;", "the cursor is the first hose the budget turned away");
                var m = System.Text.RegularExpressions.Regex.Match(src, @"public const int WalkBudget = (\d+);");
                Assert(m.Success && int.Parse(m.Groups[1].Value) >= 2 * 125 * 320, "WalkBudget covers two 125 x 320 basins");
            });
        }
    }
}
