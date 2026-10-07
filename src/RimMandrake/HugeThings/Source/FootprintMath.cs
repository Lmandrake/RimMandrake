using System;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// The pure footprint arithmetic, kept free of game state so it is the one place the shape is decided.
    /// selftest_hugethings_footprint.py mirrors every function here line for line and pins the per-species
    /// table; change one, change both.
    /// </summary>
    public static class FootprintMath
    {
        /// <summary>Round half up (never Mathf.RoundToInt, which rounds half to even).</summary>
        public static int RoundHalfUp(float v) => (int)Math.Floor(v + 0.5f);

        /// <summary>How big the plant is drawn right now, as a share of its full drawn size (0..1).</summary>
        public static float GrowthScale(float visualMin, float visualMax, float growth)
        {
            if (visualMax <= 0f) return 1f;
            float g = growth < 0f ? 0f : (growth > 1f ? 1f : growth);
            float now = visualMin + (visualMax - visualMin) * g;
            float s = now / visualMax;
            return s < 0f ? 0f : (s > 1f ? 1f : s);
        }

        /// <summary>A full-size dimension shrunk by scale; never below 1 for a non-zero dimension.</summary>
        public static int Scaled(int full, float scale)
        {
            if (full <= 0) return 0;
            return Math.Max(1, RoundHalfUp(full * scale));
        }

        /// <summary>Rect of width w and depth d whose south edge is the root row and which is centred on the
        /// root column (even widths lean east, as GenAdj.OccupiedRect does).</summary>
        public static CellRect NorthRect(IntVec3 root, int w, int d)
        {
            return new CellRect(root.x - (w - 1) / 2, root.z, w, d);
        }

        /// <summary>Rect of w x h centred on a cell (even sizes lean east/north, as GenAdj.OccupiedRect does).</summary>
        public static CellRect CentredRect(IntVec3 c, int w, int h)
        {
            return new CellRect(c.x - (w - 1) / 2, c.z - (h - 1) / 2, w, h);
        }

        /// <summary>The trunk's blocked cells for this growth, or Empty when it blocks nothing.
        /// sizeMultiplier is the Mod Settings scale.</summary>
        public static CellRect TrunkRect(IntVec3 root, RM_HugePlantExtension ext, float growthScale, float growth,
                                         float sizeMultiplier)
        {
            if (growth < ext.minGrowthToBlock) return CellRect.Empty;
            float s = growthScale * sizeMultiplier;
            int w = Scaled(ext.trunkWidth, s), d = Scaled(ext.Depth, s);
            if (w * d < 2) return CellRect.Empty;
            return NorthRect(root, w, d);
        }

        /// <summary>The click area: trunk width, running north for the drawn stem height. Null when it would be
        /// one cell (vanilla's own cell selection is then exactly right).</summary>
        public static CellRect? SelectRect(IntVec3 root, RM_HugePlantExtension ext, float growthScale, float sizeMultiplier)
        {
            float s = growthScale * sizeMultiplier;
            int w = Scaled(ext.trunkWidth, s);
            int h = Math.Max(Scaled(ext.Depth, s), Scaled(ext.Stem, s));
            if (w * h < 2) return null;
            return NorthRect(root, w, h);
        }

        /// <summary>Pawn hitbox side from a drawn size; 1 means "no bigger than vanilla".</summary>
        public static int HitboxSide(float drawn, float fraction, float multiplier)
        {
            return Math.Max(1, RoundHalfUp(drawn * fraction * multiplier));
        }
    }
}
