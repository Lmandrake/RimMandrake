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
