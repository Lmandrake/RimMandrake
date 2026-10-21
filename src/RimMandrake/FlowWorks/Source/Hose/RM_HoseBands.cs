using System.Collections.Generic;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared.Slack;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 6 (design §P5): the hose world reads depth. Every cell gets its band
    /// (HoseBandMath.Band over RM_SuperdeepTrap.StepDepthAt); a ramp (RM_PitRamp.Joins) or a ladder hung on the wall
    /// (HoseBandMath.LadderCarriesHose: raised or not) links lip and floor. The A*, the string-pull and the lay's clip test
    /// (CordWorld.StepAllowed) then refuse any other step between bands. The corridor signature carries band and links, so a
    /// newly dug square on a laid hose moves its corridor hash and the existing 250-tick check re-plans it (round the hole or
    /// down a ramp/ladder) or reels it in, once. Gate: RM_MachinerySettings.lineCrossingRulesEnabled (no new toggle).
    /// </summary>
    public static class RM_HoseBands
    {
        public static bool On => RM_MachinerySettings.lineCrossingRulesEnabled;

        /// <summary>The hose band of c (0 off the map or with the rules off).</summary>
        public static int BandAt(Map map, IntVec3 c)
        {
            if (!On || map == null || !c.InBounds(map)) return 0;
            RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
            if (eng == null || eng.ClimbCellCount == 0) return 0;
            return HoseBandMath.Band(true, RM_SuperdeepTrap.StepDepthAt(map, eng, c));
        }

        /// <summary>Phase 7, the cover gap: is c a square no hose may lie on (an intact pit cover, P2 answer 3)? StepDepthAt reads
        /// a cover as ground (band 0), so without this a hose was laid straight over one. A cover only stands over a dug square,
        /// so a cell with no climb depth costs one lookup.</summary>
        public static bool Closed(Map map, IntVec3 c)
        {
            if (!On || map == null || !c.InBounds(map)) return false;
            RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
            if (eng == null || eng.ClimbCellCount == 0 || eng.ClimbDepthAt(c) == 0) return false;
            return HoseBandMath.SurfaceClosed(true, RM_LineCrossing.SurfaceAt(map, c));
        }

        /// <summary>Do cardinal neighbours a and b (bands aB, bB, which differ) share a ramp or a hose-carrying ladder?</summary>
        public static bool Linked(Map map, IntVec3 a, IntVec3 b, int aB, int bB)
        {
            if (aB == bB) return false;
            bool ramp = RM_PitRamp.Joins(map, a, b, aB, bB);
            IntVec3 deep = aB > bB ? a : b, top = aB > bB ? b : a;
            Thing ladder = RM_LadderUtility.LadderAt(map, deep);
            RM_CompLadder comp = ladder?.TryGetComp<RM_CompLadder>();
            bool carries = ladder != null && HoseBandMath.LadderCarriesHose(true, RM_LadderUtility.HangsToward(ladder, top),
                RM_LadderUtility.Reaches(ladder), comp != null && comp.raised);
            return HoseBandMath.StepLinked(aB, bB, ramp, carries);
        }

        /// <summary>The cardinal link mask of c, as CordWorld.LinkMask numbers it (N, E, S, W = bits 0..3).</summary>
        public static int LinkMask(Map map, IntVec3 c, int band)
        {
            int m = 0;
            for (int r = 0; r < 4; r++)
            {
                var n = new IntVec3(c.x + CordWorld.CardX[r], 0, c.z + CordWorld.CardZ[r]);
                if (!n.InBounds(map)) continue;
                int nb = BandAt(map, n);
                if (nb != band && Linked(map, c, n, band, nb)) m |= 1 << r;
            }
            return m;
        }

        /// <summary>Phase 7 (P9 readout): the level changes along a lay, each counted as a ramp (RM_PitRamp.Joins) or a ladder. A
        /// diagonal step changes level through the corner the router allowed it by (CordWorld.StepAllowed), so it is judged on
        /// the cardinal pair through that corner. Nothing dug on the map: zero, one check.</summary>
        internal static void LevelChanges(Map map, IList<V2> flat, out int ramps, out int ladders)
        {
            ramps = ladders = 0;
            if (!On || map == null || flat == null || flat.Count < 2) return;
            RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
            if (eng == null || eng.ClimbCellCount == 0) return;
            // the lay is a polyline: walk each segment at 0.05 cell so no cell it passes is skipped
            Cell p0 = flat[0].Floor;
            var prev = new IntVec3(p0.X, 0, p0.Z);
            for (int i = 1; i < flat.Count; i++)
            {
                int k = System.Math.Max(1, (int)System.Math.Ceiling(V2.Dist(flat[i - 1], flat[i]) / 0.05));
                for (int j = 1; j <= k; j++)
                {
                    Cell f = (flat[i - 1] + (flat[i] - flat[i - 1]) * (j / (double)k)).Floor;
                    var c = new IntVec3(f.X, 0, f.Z);
                    if (c == prev) continue;
                    Count(map, prev, c, ref ramps, ref ladders);
                    prev = c;
                }
            }
        }

        private static void Count(Map map, IntVec3 a, IntVec3 b, ref int ramps, ref int ladders)
        {
            int aB = BandAt(map, a), bB = BandAt(map, b);
            if (aB == bB) return;
            if (a.x != b.x && a.z != b.z)
            {
                // diagonal: through the corner on a's band (then the change is corner -> b) or on b's band (a -> corner)
                foreach (IntVec3 k in new[] { new IntVec3(a.x, 0, b.z), new IntVec3(b.x, 0, a.z) })
                {
                    int kB = BandAt(map, k);
                    if (kB == aB) { a = k; break; }
                    if (kB == bB) { b = k; break; }
                }
                aB = BandAt(map, a); bB = BandAt(map, b);
                if (aB == bB) return;
            }
            if (RM_PitRamp.Joins(map, a, b, aB, bB)) ramps++;
            else if (Linked(map, a, b, aB, bB)) ladders++;   // not linked at all: an old lay the router never made; say nothing
        }

        /// <summary>Writes bands and links into a fresh hose world (World()). Only dug squares and their neighbours can differ
        /// from band 0, so a map with nothing dug costs one check.</summary>
        internal static void Apply(Map map, CordWorld w)
        {
            if (!On || map == null) return;
            RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
            if (eng == null || eng.ClimbCellCount == 0) return;
            int W = map.Size.x, H = map.Size.z;
            var dug = new List<IntVec3>();
            for (int z = 0; z < H; z++)
                for (int x = 0; x < W; x++)
                {
                    var c = new IntVec3(x, 0, z);
                    // phase 7: an intact pit cover carries no hose (P2 answer 3), so it is closed like a wall
                    if (eng.ClimbDepthAt(c) > 0 && HoseBandMath.SurfaceClosed(true, RM_LineCrossing.SurfaceAt(map, c)))
                        w.SetBlocked(new Cell(x, z), BlockKind.Wall);
                    int b = HoseBandMath.Band(true, RM_SuperdeepTrap.StepDepthAt(map, eng, c));
                    if (b == 0) continue;
                    w.SetBand(new Cell(x, z), b);
                    dug.Add(c);
                }
            foreach (IntVec3 c in dug)
            {
                int b = w.BandAt(new Cell(c.x, c.z));
                for (int r = 0; r < 4; r++)
                {
                    var n = new IntVec3(c.x + CordWorld.CardX[r], 0, c.z + CordWorld.CardZ[r]);
                    if (!n.InBounds(map)) continue;
                    int nb = w.BandAt(new Cell(n.x, n.z));
                    if (nb != b && Linked(map, c, n, b, nb)) w.LinkBands(new Cell(c.x, c.z), new Cell(n.x, n.z));
                }
            }
        }
    }
}
