using System;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// The pure footprint arithmetic, kept free of game state so it is the one place the shape is decided.
    /// The arithmetic is Kernel/RM_FootprintKernel.cs (Verse-free); this class only converts to CellRect/IntVec3.
    /// SelfTest/HugeThingsFuzz.cs fuzzes the kernel; selftest_hugethings_footprint.py pins the per-species table.
    /// </summary>
    public static class FootprintMath
    {
        private static CellRect R(RM_KRect r) { return new CellRect(r.minX, r.minZ, r.w, r.h); }
        private static RM_KRect K(CellRect r) { return new RM_KRect(r.minX, r.minZ, r.Width, r.Height); }

        /// <summary>Round half up (never Mathf.RoundToInt, which rounds half to even).</summary>
        public static int RoundHalfUp(float v) => RM_FootprintKernel.RoundHalfUp(v);

        /// <summary>How big the plant is drawn right now, as a share of its full drawn size (0..1).</summary>
        public static float GrowthScale(float visualMin, float visualMax, float growth) => RM_FootprintKernel.GrowthScale(visualMin, visualMax, growth);

        /// <summary>A full-size dimension shrunk by scale; never below 1 for a non-zero dimension.</summary>
        public static int Scaled(int full, float scale) => RM_FootprintKernel.Scaled(full, scale);

        /// <summary>Rect of width w and depth d whose south edge is the root row and which is centred on the
        /// root column (even widths lean east, as GenAdj.OccupiedRect does).</summary>
        public static CellRect NorthRect(IntVec3 root, int w, int d) => R(RM_FootprintKernel.NorthRect(root.x, root.z, w, d));

        /// <summary>Rect of w x h centred on a cell (even sizes lean east/north, as GenAdj.OccupiedRect does).</summary>
        public static CellRect CentredRect(IntVec3 c, int w, int h) => R(RM_FootprintKernel.CentredRect(c.x, c.z, w, h));

        /// <summary>The trunk's blocked cells for this growth, or Empty when it blocks nothing.
        /// sizeMultiplier is the Mod Settings scale.</summary>
        public static CellRect TrunkRect(IntVec3 root, RM_HugePlantExtension ext, float growthScale, float growth,
                                         float sizeMultiplier)
        {
            RM_KRect r = RM_FootprintKernel.TrunkRect(root.x, root.z, ext.trunkWidth, ext.trunkDepth, ext.minGrowthToBlock, growthScale, growth, sizeMultiplier);
            return r.IsEmpty ? CellRect.Empty : R(r);
        }

        /// <summary>The click area: trunk width, running north for the drawn stem height. Null when it would be
        /// one cell (vanilla's own cell selection is then exactly right).</summary>
        public static CellRect? SelectRect(IntVec3 root, RM_HugePlantExtension ext, float growthScale, float sizeMultiplier)
        {
            RM_KRect r = RM_FootprintKernel.SelectRect(root.x, root.z, ext.trunkWidth, ext.trunkDepth, ext.stemHeight, growthScale, sizeMultiplier);
            return r.IsEmpty ? (CellRect?)null : R(r);
        }

        /// <summary>The largest rect any setting could ask for, for re-linking after load.</summary>
        public static CellRect MaxRect(IntVec3 root, RM_HugePlantExtension ext) => R(RM_FootprintKernel.MaxRect(root.x, root.z, ext.trunkWidth, ext.trunkDepth));

        /// <summary>Pawn hitbox side from a drawn size; 1 means "no bigger than vanilla".</summary>
        public static int HitboxSide(float drawn, float fraction, float multiplier) => RM_FootprintKernel.HitboxSide(drawn, fraction, multiplier);

        public static CellRect Union(CellRect a, CellRect b) => R(RM_FootprintKernel.Union(K(a), K(b)));

        /// <summary>The pawn's click hitbox, or null for "no bigger than vanilla".</summary>
        public static CellRect? PawnHitbox(float drawnX, float drawnY, float fraction, float multiplier, CellRect foot, IntVec3 drawCell)
        {
            RM_KRect r = RM_FootprintKernel.PawnHitbox(drawnX, drawnY, fraction, multiplier, K(foot), drawCell.x, drawCell.z);
            return r.IsEmpty ? (CellRect?)null : R(r);
        }
    }
}
