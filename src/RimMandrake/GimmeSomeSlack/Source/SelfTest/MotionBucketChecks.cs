// CORD_GRAPH_TOPOLOGY_REVISION_1 (perf half): DrawMotion's per-material buckets (_Shared/SlackGeometry/DrawOrder.cs MaterialBuckets)
// must draw exactly what the old filtered full scan drew, in the same order, for every material index.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class MotionBucketChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "motionbuckets: " + msg);

        private static List<int> OldScan(List<int> items, Func<int, int> idx, int nv, int v) =>
            items.Where(p => !(nv > 1 && idx(p) != v)).ToList();

        /// <summary>Owner 2026-11-07: the spark follows the writhing end. The tail's outer point IS the end's tip on a laid live end, so
        /// RideTail finds it; the point it hands back is the one the whip bent.</summary>
        internal static void SparkRidesTail()
        {
            var w = new CordWorld(40, 20);
            for (int x = 5; x <= 25; x++) w.SetConduit(new Cell(x, 10));
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, new BuildOptions(), c => true);
            int ends = 0, far = 0, stays = 0;
            foreach (LaidPiece p in ps)
                foreach (CordEnd e in p.Ends)
                {
                    if (e.Wall) continue;
                    ends++;
                    var laid = new List<V2>(); var now = new List<V2>();
                    foreach (CordStrand s in p.Strands)
                    {
                        if (s.WhipA > 0) { laid.Add(s.Pts[0]); now.Add(s.Pts[0] + new V2(0.2, -0.1)); }
                        if (s.WhipB > 0) { laid.Add(s.Pts[s.Pts.Count - 1]); now.Add(s.Pts[s.Pts.Count - 1] + new V2(0.2, -0.1)); }
                    }
                    V2 got = CordMotion.RideTail(e.Tip, laid, now);
                    if (Math.Abs(got.X - e.Tip.X - 0.2) > 1e-6 || Math.Abs(got.Z - e.Tip.Z + 0.1) > 1e-6) far++;
                    V2 alone = CordMotion.RideTail(e.Tip, new List<V2>(), new List<V2>());
                    if (alone.X != e.Tip.X || alone.Z != e.Tip.Z) stays++;
                }
            Check(ends >= 2, "a cut run lays its live ends (" + ends + ")");
            Check(far == 0, "the spark of a live end rides its own whip tail (" + far + "/" + ends + " do not)");
            Check(stays == 0, "no tail drawn: the spark stays on the laid tip");
        }

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
