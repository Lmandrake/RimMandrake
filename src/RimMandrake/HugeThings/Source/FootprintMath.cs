using System.Collections.Generic;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// The Verse adapter over Kernel/RM_HugeFootprintKernel.cs, which holds every decision (and the measured draw
    /// transform, with the decompiled methods it was read from). Nothing here but type conversion.
    /// </summary>
    public static class FootprintMath
    {
        public static HugeQuad Quad(IntVec3 root, float drawSizeX, float visual, float jitterX, float jitterZ)
            => RM_HugeFootprintKernel.Quad(root.x, root.z, drawSizeX, visual, jitterX, jitterZ);

        public static CellRect PictureRect(HugeQuad q, HugeMask m, bool flip) => ToRect(RM_HugeFootprintKernel.PictureBox(q, m, flip));

        public static List<IntVec3> ContactCells(IntVec3 root, HugeQuad q, float blockScale, bool flip, HugeMask m)
        {
            List<long> keys = RM_HugeFootprintKernel.ContactCells(root.x, root.z, q, blockScale, flip, m);
            List<IntVec3> cells = new List<IntVec3>(keys.Count);
            for (int i = 0; i < keys.Count; i++) cells.Add(new IntVec3(RM_HugeFootprintKernel.KeyX(keys[i]), 0, RM_HugeFootprintKernel.KeyZ(keys[i])));
            return cells;
        }

        public static CellRect SelectRect(IntVec3 root, HugeQuad q, HugeMask m, bool flip, List<IntVec3> blocked)
        {
            List<long> keys = new List<long>(blocked.Count);
            for (int i = 0; i < blocked.Count; i++) keys.Add(RM_HugeFootprintKernel.Key(blocked[i].x, blocked[i].z));
            return ToRect(RM_HugeFootprintKernel.SelectBox(root.x, root.z, RM_HugeFootprintKernel.PictureBox(q, m, flip), keys));
        }

        public static CellRect CentredRect(IntVec3 c, int w, int h) => ToRect(RM_HugeFootprintKernel.CentredBox(c.x, c.z, w, h));

        public static int HitboxSide(float drawn, float fraction, float multiplier)
            => RM_HugeFootprintKernel.HitboxSide(drawn, fraction, multiplier);

        public static CellRect Union(CellRect a, CellRect b) => ToRect(RM_HugeFootprintKernel.Union(FromRect(a), FromRect(b)));

        /// <summary>The pawn's click hitbox, or null for "no bigger than vanilla".</summary>
        public static CellRect? PawnHitbox(float drawnX, float drawnY, float fraction, float multiplier, CellRect foot, IntVec3 drawCell)
        {
            return RM_HugeFootprintKernel.PawnHitbox(drawnX, drawnY, fraction, multiplier, FromRect(foot), drawCell.x, drawCell.z, out CellBox b)
                ? ToRect(b) : (CellRect?)null;
        }

        private static CellBox FromRect(CellRect r) => new CellBox(r.minX, r.minZ, r.maxX, r.maxZ);

        private static CellRect ToRect(CellBox b) => CellRect.FromLimits(b.MinX, b.MinZ, b.MaxX, b.MaxZ);
    }
}
