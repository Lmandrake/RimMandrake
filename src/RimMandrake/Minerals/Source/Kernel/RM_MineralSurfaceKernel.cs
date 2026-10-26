// Verse-free kernel of the surface adapter (MINERAL_SURFACE_BUILD_PER_BIOME, minerals registry design §4 and §6.3).
// RM_MineralSurface feeds it the policy's decisions and the map's numbers; SelfTest compiles this file alone, so keep it free of
// Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Minerals
{
    /// <summary>One registry material the surface adapter places, with the mineables a lump may be made of (weighted by their
    /// ORIGINAL scatter, so a row naming two vein defs keeps the split their mods gave them).</summary>
    public sealed class SurfaceTarget
    {
        public string MaterialId;
        public float UnitsPerCell;
        public readonly List<KeyValuePair<string, float>> Mineables = new List<KeyValuePair<string, float>>();
    }

    public static class RM_MineralSurfaceKernel
    {
        public const float ReferenceBlotchesPer10k = 11f;   // design §4: EPM is stated for a "large hills" map
        public const float ReferenceMapCells = 62500f;      // 250 x 250

        /// <summary>The surface adapter can place a row only when its number is EPM with a yield per cell to convert it.</summary>
        public static bool Placeable(MineralRow row)
        {
            return row != null && row.Unit == "EPM" && row.UnitsPerCellOrFind > 0f;
        }

        /// <summary>Expected lumps on one map: EPM (already times overrides and the vein multiplier) x hilliness policy (blotches/11)
        /// x area (cells/62,500) x nomadic factor, over units per lump (units per cell x 30 mean cells).</summary>
        public static float ExpectedLumps(float epm, float unitsPerCell, float blotchesPer10k, int mapCells, float nomadicFactor)
        {
            if (!(epm > 0f) || !(unitsPerCell > 0f) || !(blotchesPer10k > 0f) || mapCells <= 0 || !(nomadicFactor > 0f)) return 0f;
            return epm * (blotchesPer10k / ReferenceBlotchesPer10k) * (mapCells / ReferenceMapCells) * nomadicFactor
                 / (unitsPerCell * RM_MineralPolicyKernel.MeanLumpCells);
        }

        /// <summary>Stochastic rounding (design §4, GPT 1.1): floor(x) plus one with probability frac(x). <paramref name="u"/> in [0,1).</summary>
        public static int StochasticRound(float x, double u)
        {
            if (!(x > 0f)) return 0;
            int whole = (int)Math.Floor(x);
            return whole + (u < x - whole ? 1 : 0);
        }

        /// <summary>Share of vanilla's own weighted scatter that is still live: sum of current scatter over the sum of original scatter,
        /// both over the defs vanilla's ChooseThingDef may pick on this map (value cap applied by the caller). Vanilla picks each lump
        /// by RELATIVE weight, so zeroing governed veins without scaling the lump count hands their lumps to whatever is left: an
        /// unregistered steel would gain every lump components and plasteel lost, against the owner card ("an ore the registry has
        /// never heard of behaves as its mod intended"). Scaling the count by this share keeps each kept def's expected lumps.</summary>
        public static float KeptShare(IEnumerable<KeyValuePair<float, float>> currentOriginal)
        {
            double cur = 0, orig = 0;
            foreach (KeyValuePair<float, float> kv in currentOriginal)
            {
                if (kv.Key > 0f) cur += kv.Key;
                if (kv.Value > 0f) orig += kv.Value;
            }
            if (!(orig > 0)) return 1f;   // vanilla had nothing to pick from: nothing to keep
            return (float)Math.Min(1.0, cur / orig);
        }

        /// <summary>Expected lumps of one def from vanilla's weighted scatter: count x weight / sum of weights.</summary>
        public static float ExpectedVanillaLumps(float count, float weight, float weightSum)
        {
            if (!(weightSum > 0f) || !(weight > 0f)) return 0f;
            return count * weight / weightSum;
        }

        /// <summary>The materials to place and their mineables: every decision the policy marked SurfacePlaced, grouped by row.</summary>
        public static List<SurfaceTarget> SurfaceTargets(IList<MineralRow> rows, IEnumerable<PolicyDecision> decisions,
                                                         IDictionary<string, MineralDefInfo> originals)
        {
            var byId = new Dictionary<string, MineralRow>();
            foreach (MineralRow r in rows) if (r != null && r.MaterialId != null && !byId.ContainsKey(r.MaterialId)) byId[r.MaterialId] = r;
            var outMap = new Dictionary<string, SurfaceTarget>();
            var order = new List<SurfaceTarget>();
            foreach (PolicyDecision p in decisions)
            {
                if (p == null || !p.SurfacePlaced || p.MaterialId == null) continue;
                if (!byId.TryGetValue(p.MaterialId, out MineralRow row) || !Placeable(row)) continue;
                if (originals == null || !originals.TryGetValue(p.DefName, out MineralDefInfo o) || !(o.Scatter > 0f)) continue;
                if (!outMap.TryGetValue(p.MaterialId, out SurfaceTarget t))
                {
                    t = new SurfaceTarget { MaterialId = p.MaterialId, UnitsPerCell = row.UnitsPerCellOrFind };
                    outMap[p.MaterialId] = t;
                    order.Add(t);
                }
                t.Mineables.Add(new KeyValuePair<string, float>(p.DefName, o.Scatter));
            }
            order.Sort((a, b) => string.CompareOrdinal(a.MaterialId, b.MaterialId));
            return order;
        }

        /// <summary>Weighted pick of a lump's mineable; null when nothing has weight. <paramref name="u"/> in [0,1].</summary>
        public static string PickMineable(IList<KeyValuePair<string, float>> mineables, double u)
        {
            double total = 0;
            foreach (KeyValuePair<string, float> kv in mineables) if (kv.Value > 0f) total += kv.Value;
            if (!(total > 0)) return null;
            double at = u * total, run = 0;
            string last = null;
            foreach (KeyValuePair<string, float> kv in mineables)
            {
                if (!(kv.Value > 0f)) continue;
                run += kv.Value; last = kv.Key;
                if (at < run) return kv.Key;
            }
            return last;
        }

        /// <summary>Design §4 diagnostic: ore cells placed per 1,000 natural-rock cells, so a rock-poor shortfall is visible.</summary>
        public static float OrePer1000Rock(int oreCells, int rockCells)
        {
            if (rockCells <= 0) return 0f;
            return 1000f * oreCells / rockCells;
        }
    }
}
