// Verse-free kernel of Huge Things: the footprint arithmetic (rounding, growth scale, trunk / click / hitbox rects), the trunk-blocker
// reconcile plan, and the cell-eligibility rule. FootprintMath, CompHugeFootprint and HugeThingsApi call these with the same
// expressions; SelfTest/HugeThingsFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a
// `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>A cell rectangle: south-west corner plus width and depth. Empty = no cells (width or depth <= 0).</summary>
    public struct RM_KRect
    {
        public int minX, minZ, w, h;
        public RM_KRect(int minX, int minZ, int w, int h) { this.minX = minX; this.minZ = minZ; this.w = w; this.h = h; }
        public static RM_KRect Empty { get { return new RM_KRect(0, 0, 0, 0); } }
        public bool IsEmpty { get { return w <= 0 || h <= 0; } }
        public int MaxX { get { return minX + w - 1; } }
        public int MaxZ { get { return minZ + h - 1; } }
        public int Area { get { return IsEmpty ? 0 : w * h; } }
        public bool Contains(int x, int z) { return !IsEmpty && x >= minX && x <= MaxX && z >= minZ && z <= MaxZ; }
        public RM_KRect ExpandedBy(int n) { return new RM_KRect(minX - n, minZ - n, w + n * 2, h + n * 2); }
    }

    /// <summary>What the trunk reconcile decided: positions of existing blockers to remove, cells to grow a new blocker on.</summary>
    public sealed class RM_TrunkPlan
    {
        public List<int> destroyIndexes = new List<int>();
        public List<long> spawnCells = new List<long>();
    }

    public static class RM_FootprintKernel
    {
        /// <summary>The Mod Settings ceiling for the trunk-size slider; MaxRect (re-linking after load) must cover it.</summary>
        public const float MaxTrunkScale = 1.5f;
        /// <summary>Default share of a huge pawn's drawn size that counts as body (PROVISIONAL tuning).</summary>
        public const float DefaultHitboxFraction = 0.6f;
        /// <summary>Default growth below which a plant blocks nothing (PROVISIONAL tuning).</summary>
        public const float DefaultMinGrowthToBlock = 0.25f;

        /// <summary>The settings sliders stop at 0.5..1.5, but the file can be edited: a larger value must not outgrow MaxRect (re-link after load would then miss blockers).</summary>
        public static float ClampScale(float m) { return m < 0f ? 0f : (m > MaxTrunkScale ? MaxTrunkScale : m); }

        public static long Pack(int x, int z) { return ((long)x << 32) | (uint)z; }
        public static int PackedX(long k) { return (int)(k >> 32); }
        public static int PackedZ(long k) { return (int)(uint)(k & 0xFFFFFFFFL); }

        /// <summary>Round half up (never banker's).</summary>
        public static int RoundHalfUp(float v) { return (int)Math.Floor(v + 0.5f); }

        public static int DepthOf(int trunkWidth, int trunkDepth) { return trunkDepth > 0 ? trunkDepth : trunkWidth; }
        public static int StemOf(int trunkWidth, int trunkDepth, int stemHeight) { return stemHeight > 0 ? stemHeight : DepthOf(trunkWidth, trunkDepth); }

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

        /// <summary>Rect of width w and depth d whose south edge is the root row, centred on the root column (even widths lean east).</summary>
        public static RM_KRect NorthRect(int rootX, int rootZ, int w, int d) { return new RM_KRect(rootX - (w - 1) / 2, rootZ, w, d); }

        /// <summary>Rect of w x h centred on a cell (even sizes lean east/north).</summary>
        public static RM_KRect CentredRect(int cx, int cz, int w, int h) { return new RM_KRect(cx - (w - 1) / 2, cz - (h - 1) / 2, w, h); }

        /// <summary>The trunk's blocked cells for this growth, or Empty when it blocks nothing.</summary>
        public static RM_KRect TrunkRect(int rootX, int rootZ, int trunkWidth, int trunkDepth, float minGrowthToBlock, float growthScale, float growth, float sizeMultiplier)
        {
            if (growth < minGrowthToBlock) return RM_KRect.Empty;
            float s = growthScale * ClampScale(sizeMultiplier);
            int w = Scaled(trunkWidth, s), d = Scaled(DepthOf(trunkWidth, trunkDepth), s);
            if (w * d < 2) return RM_KRect.Empty;
            return NorthRect(rootX, rootZ, w, d);
        }

        /// <summary>The click area: trunk width, running north for the drawn stem height. Empty when it would be one cell.</summary>
        public static RM_KRect SelectRect(int rootX, int rootZ, int trunkWidth, int trunkDepth, int stemHeight, float growthScale, float sizeMultiplier)
        {
            float s = growthScale * ClampScale(sizeMultiplier);
            int w = Scaled(trunkWidth, s);
            int h = Math.Max(Scaled(DepthOf(trunkWidth, trunkDepth), s), Scaled(StemOf(trunkWidth, trunkDepth, stemHeight), s));
            if (w * h < 2) return RM_KRect.Empty;
            return NorthRect(rootX, rootZ, w, h);
        }

        /// <summary>The largest rect any setting could ask for, for re-linking blockers after load.</summary>
        public static RM_KRect MaxRect(int rootX, int rootZ, int trunkWidth, int trunkDepth)
        {
            int w = Scaled(trunkWidth, MaxTrunkScale);
            int d = Scaled(DepthOf(trunkWidth, trunkDepth), MaxTrunkScale);
            return NorthRect(rootX, rootZ, w, d).ExpandedBy(1);
        }

        /// <summary>Pawn hitbox side from a drawn size; 1 means "no bigger than vanilla".</summary>
        public static int HitboxSide(float drawn, float fraction, float multiplier) { return Math.Max(1, RoundHalfUp(drawn * fraction * ClampScale(multiplier))); }

        public static RM_KRect Union(RM_KRect a, RM_KRect b)
        {
            int minX = Math.Min(a.minX, b.minX), minZ = Math.Min(a.minZ, b.minZ);
            int maxX = Math.Max(a.MaxX, b.MaxX), maxZ = Math.Max(a.MaxZ, b.MaxZ);
            return new RM_KRect(minX, minZ, maxX - minX + 1, maxZ - minZ + 1);
        }

        /// <summary>
        /// The click hitbox of a huge pawn: Empty when the body is no bigger than its footprint and the footprint is a single cell
        /// (vanilla is then right), the footprint itself when the body fits inside it, else the union of body and footprint.
        /// </summary>
        public static RM_KRect PawnHitbox(float drawnX, float drawnY, float fraction, float multiplier, RM_KRect foot, int drawCellX, int drawCellZ)
        {
            int w = HitboxSide(drawnX, fraction, multiplier);
            int h = HitboxSide(drawnY, fraction, multiplier);
            if (w <= foot.w && h <= foot.h) return foot.Area > 1 ? foot : RM_KRect.Empty;
            return Union(CentredRect(drawCellX, drawCellZ, w, h), foot);
        }

        /// <summary>
        /// Bring the blockers in line with the wanted trunk: remove every live blocker outside it (all of them when it is empty), then
        /// grow a blocker on every wanted cell that is in the map, is not the plant's own cell, has no blocker of ours yet and can take one.
        /// </summary>
        public static RM_TrunkPlan Plan(RM_KRect want, int rootX, int rootZ, IList<long> liveBlockerCells, Func<int, int, bool> inBounds, Func<int, int, bool> cellTakesTrunk)
        {
            var plan = new RM_TrunkPlan();
            var have = new HashSet<long>();
            for (int i = 0; i < liveBlockerCells.Count; i++)
            {
                long k = liveBlockerCells[i];
                if (want.IsEmpty || !want.Contains(PackedX(k), PackedZ(k))) plan.destroyIndexes.Add(i);
                else have.Add(k);
            }
            if (want.IsEmpty) return plan;
            for (int z = want.minZ; z <= want.MaxZ; z++)
                for (int x = want.minX; x <= want.MaxX; x++)
                {
                    if ((x == rootX && z == rootZ) || !inBounds(x, z) || have.Contains(Pack(x, z))) continue;
                    if (!cellTakesTrunk(x, z)) continue;
                    plan.spawnCells.Add(Pack(x, z));
                }
            return plan;
        }

        /// <summary>
        /// A trunk grows only into cells it can take without destroying anything that matters: walkable ground, no pawn, no building
        /// (another trunk included), no blueprint or frame, nothing indestructible, no tree and no other huge plant.
        /// </summary>
        public static bool CellTakesTrunk(bool walkable, bool hasPawn, bool hasBuilding, bool hasBlueprintOrFrame, bool hasIndestructible, bool hasTreeOrHugePlant)
        {
            return walkable && !hasPawn && !hasBuilding && !hasBlueprintOrFrame && !hasIndestructible && !hasTreeOrHugePlant;
        }
    }
}
