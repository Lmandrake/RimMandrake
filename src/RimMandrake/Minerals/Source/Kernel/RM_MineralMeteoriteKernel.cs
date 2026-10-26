// Verse-free kernel of the meteorite adapter (MINERAL_ADAPTERS_BUILD_DONOR_SOURCES R5; owner card 2026-10-25 "Which materials may
// fall in meteorites? -> Only metals and space-ish ores": stone types never fall). RM_MineralMeteorite feeds it the vanilla
// ThingSetMaker_Meteorite.nonSmoothedMineables and the generated whitelist (RM_MineralMeteorites, the CSV's meteoritic=yes rows);
// SelfTest compiles this file alone, so keep it free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Minerals
{
    /// <summary>One mineable vanilla's meteorite list holds: its defName, building.isResourceRock and the market value of what it yields.</summary>
    public sealed class MeteorCandidate
    {
        public string DefName;
        public bool ResourceRock;
        public float YieldValue;

        public MeteorCandidate(string defName, bool resourceRock, float yieldValue)
        {
            DefName = defName; ResourceRock = resourceRock; YieldValue = yieldValue;
        }
    }

    public sealed class MeteorFilter
    {
        public readonly List<string> Kept = new List<string>();      // vanilla order
        public readonly List<string> Dropped = new List<string>();
        /// <summary>Master toggle on but nothing of the whitelist is in the game: the vanilla list is kept, because an empty list makes
        /// every meteorite throw (vanilla RandomElement of nothing is null, then ThingMaker.MakeThing(null)).</summary>
        public bool FellBack;
        /// <summary>The adapter picks meteorite contents itself (RM_MineralMeteoriteKernel.Pick) only while this is true.</summary>
        public bool Active;
    }

    public static class RM_MineralMeteoriteKernel
    {
        public const float PreciousValue = 5f;                                // ThingSetMaker_Meteorite.PreciousMineableMarketValue
        public static readonly float[] VanillaBucketWeights = { 0.4f, 0.35f, 0.25f };   // rock, cheap ore, precious ore (FindRandomMineableDef)

        /// <summary>What stays in nonSmoothedMineables. Master toggle off = the vanilla list untouched. On = the vanilla list (so a def
        /// vanilla bars, mineablePreventMeteorite or smoothed, stays barred) intersected with the whitelist, and never a def that is not a
        /// resource rock: that is a stone type, and a whitelist naming one is a registry defect this refuses rather than ships.</summary>
        public static MeteorFilter Filter(IList<MeteorCandidate> vanilla, ICollection<string> whitelist, bool enabled)
        {
            var f = new MeteorFilter();
            foreach (MeteorCandidate c in vanilla)
            {
                if (c == null || c.DefName == null) continue;
                bool keep = !enabled || (c.ResourceRock && whitelist != null && whitelist.Contains(c.DefName));
                (keep ? f.Kept : f.Dropped).Add(c.DefName);
            }
            if (enabled && f.Kept.Count == 0)
            {
                f.FellBack = true;
                f.Dropped.Clear();
                foreach (MeteorCandidate c in vanilla) if (c != null && c.DefName != null) f.Kept.Add(c.DefName);
            }
            f.Active = enabled && !f.FellBack;
            return f;
        }

        /// <summary>0 = not a resource rock (stone), 1 = ore yielding under PreciousValue, 2 = precious ore: vanilla's three buckets.</summary>
        public static int Bucket(MeteorCandidate c)
        {
            if (!c.ResourceRock) return 0;
            return c.YieldValue < PreciousValue ? 1 : 2;
        }

        /// <summary>Vanilla's draw with its bucket weights renormalised over the buckets that still hold something. Vanilla rolls a bucket
        /// first and picks inside it, so once stone types are gone its 40% rock roll would pick from nothing and the meteorite would throw;
        /// here an empty bucket's share goes to the others in proportion. Null only for an empty list.</summary>
        public static MeteorCandidate Pick(IList<MeteorCandidate> list, float bucketRoll, float indexRoll)
        {
            var buckets = new List<MeteorCandidate>[3] { new List<MeteorCandidate>(), new List<MeteorCandidate>(), new List<MeteorCandidate>() };
            foreach (MeteorCandidate c in list) if (c != null) buckets[Bucket(c)].Add(c);
            float total = 0f;
            for (int b = 0; b < 3; b++) if (buckets[b].Count > 0) total += VanillaBucketWeights[b];
            if (total <= 0f) return null;
            float roll = Clamp01(bucketRoll) * total;
            int chosen = -1;
            for (int b = 0; b < 3; b++)
            {
                if (buckets[b].Count == 0) continue;
                chosen = b;
                if (roll < VanillaBucketWeights[b]) break;
                roll -= VanillaBucketWeights[b];
            }
            List<MeteorCandidate> l = buckets[chosen];
            return l[Math.Min((int)(Clamp01(indexRoll) * l.Count), l.Count - 1)];
        }

        /// <summary>The chance each bucket gets under Pick (diagnostic and selftest).</summary>
        public static float[] BucketShares(IList<MeteorCandidate> list)
        {
            var has = new bool[3];
            foreach (MeteorCandidate c in list) if (c != null) has[Bucket(c)] = true;
            float total = 0f;
            for (int b = 0; b < 3; b++) if (has[b]) total += VanillaBucketWeights[b];
            var s = new float[3];
            for (int b = 0; b < 3; b++) s[b] = has[b] && total > 0f ? VanillaBucketWeights[b] / total : 0f;
            return s;
        }

        private static float Clamp01(float v) { return v < 0f ? 0f : v > 1f ? 1f : v; }
    }
}
