// CORD_GRAPH_TOPOLOGY_REVISION_1 (perf half): DrawMotion's per-material buckets (../Core/DrawOrder.cs MaterialBuckets)
// must draw exactly what the old filtered full scan drew, in the same order, for every material index.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class MotionBucketChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "motionbuckets: " + msg);

        private static List<int> OldScan(List<int> items, Func<int, int> idx, int nv, int v) =>
            items.Where(p => !(nv > 1 && idx(p) != v)).ToList();

        public static void Run()
        {
            var rng = new Random(20261010);
            int mism = 0, cases = 0;
            foreach (int nv in new[] { 1, 2, 5, 16 })
                for (int trial = 0; trial < 50; trial++)
                {
                    var items = Enumerable.Range(0, rng.Next(0, 300)).ToList();
                    var map = items.ToDictionary(i => i, i => rng.Next(-1, nv + 2));   // some out of range on purpose
                    Func<int, int> idx = i => map[i];
                    List<int>[] b = MaterialBuckets.By(items, idx, nv);
                    for (int v = 0; v < nv; v++)
                    {
                        cases++;
                        if (!b[v].SequenceEqual(OldScan(items, idx, nv, v))) mism++;
                    }
                }
            Check(mism == 0, "buckets == old filtered scan, same order, over " + cases + " (nv, v) cases (" + mism + " mismatched)");
            var one = MaterialBuckets.By(new List<int> { 3, 1, 2 }, i => 99, 1);
            Check(one.Length == 1 && one[0].SequenceEqual(new[] { 3, 1, 2 }), "nv 1 draws everything in bucket 0 whatever the index");
            Check(MaterialBuckets.By<int>(null, i => 0, 4).All(l => l.Count == 0), "no pieces, empty buckets");
            // can-fail: a bucketer that sorted by index within a bucket, or kept out-of-range pieces, would differ
            var items2 = new List<int> { 5, 2, 9 };
            Func<int, int> id2 = i => i == 9 ? 7 : 0;
            Check(!MaterialBuckets.By(items2, id2, 2)[0].Contains(9) && MaterialBuckets.By(items2, id2, 2)[0].SequenceEqual(new[] { 5, 2 }),
                  "can-fail: an out-of-range index is dropped and the order is not sorted");
        }
    }

    /// <summary>Design §5 per-def conduit toggles (built 2026-10-10): Core/ConduitTargets.cs.</summary>
    internal static class ConduitTargetChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "conduittargets: " + msg);

        public static void Run()
        {
            var cands = new[] { "PowerConduit", "WaterproofConduit", "VFEP_LEDConduit" };
            Check(ConduitTargets.Select(cands, new List<string>()).SequenceEqual(cands), "nothing unticked: every candidate is a target (shipped behaviour)");
            Check(ConduitTargets.Select(cands, null).SequenceEqual(cands), "a null list (old settings file) behaves as nothing unticked");
            var ex = new List<string>();
            ConduitTargets.Toggle(ex, "WaterproofConduit", false);
            Check(ConduitTargets.Select(cands, ex).SequenceEqual(new[] { "PowerConduit", "VFEP_LEDConduit" }), "unticking waterproof removes only it");
            ConduitTargets.Toggle(ex, "WaterproofConduit", false);
            Check(ex.Count == 1, "unticking twice stores it once");
            ConduitTargets.Toggle(ex, "WaterproofConduit", true);
            Check(ex.Count == 0 && ConduitTargets.Select(cands, ex).Count == 3, "ticking it again restores it");
            Check(ConduitTargets.Select(cands, new List<string> { "NotInstalledConduit" }).Count == 3, "a stale defName from a removed mod is harmless");
        }
    }
}
