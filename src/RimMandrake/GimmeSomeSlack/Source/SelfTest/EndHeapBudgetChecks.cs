// GSS_END_HEAPS_FIX_BYPASS_LOOP_BUDGET (GPT review FB_hose_gss_3.3, 2026-10-23): the long-run end heaps of CordLayer.AddLoops
// were spliced without the target budget the ordinary loops honour, and the settle's rest-length clamp keeps whatever was
// sprawled. Scene (the finding's reproduction): a 45-cell straight cord on open ground, slack target 47 (a two-cell budget),
// default LayParams. Can-fail: the same lays with a roomy target (200) DO overspend 47 x 1.25, so the end heaps still form
// and the bound below is not vacuous.
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class EndHeapBudgetChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "end-heap budget: " + msg);

        private static List<V2> Lay(double target, int seed, out SettleStats st)
        {
            var Q = new List<V2>();
            for (double x = 2; x <= 47.0001; x += 0.05) Q.Add(new V2(x, 10.5));
            var ramp = new double[Q.Count];
            for (int i = 0; i < ramp.Length; i++) ramp[i] = 1;
            st = new SettleStats();
            return CordLayer.AddLoops(new CordWorld(60, 22), Q, ramp, new LayParams(), CordRng.Of(seed, "endheap"), target, st);
        }

        public static void Run()
        {
            const double tight = 47, bar = tight * 1.25;
            double worstTight = 0, worstRoomy = 0;
            int heapsTight = 0, heapsRoomy = 0;
            for (int seed = 1; seed <= 40; seed++)
            {
                worstTight = System.Math.Max(worstTight, Geo.Length(Lay(tight, seed, out SettleStats a)));
                heapsTight += a.EndHeaps;
                worstRoomy = System.Math.Max(worstRoomy, Geo.Length(Lay(200, seed, out SettleStats b)));
                heapsRoomy += b.EndHeaps;
            }
            Check(worstRoomy > bar, $"can-fail: with a roomy target the end heaps carry a 45-cell cord to {worstRoomy:0.0} > {bar:0.0} cells ({heapsRoomy} end heaps in 40 lays)");
            // the budget is charged with the shape's own length; the two joins a splice adds can run a few samples over it
            Check(worstTight <= bar + 0.5, $"a 45-cell cord with target {tight} stays within {bar:0.0} (+0.5 splice joins) cells after loops and end heaps (worst {worstTight:0.0}, {heapsTight} end heaps in 40 lays)");
            Check(!CordLayer.OverBudget(40, new List<V2> { new V2(0, 0), new V2(1, 0) }, 40), "a 1-cell shape on a 40-cell cord fits a target of 40 (41 <= 50)");
            Check(CordLayer.OverBudget(40, new List<V2> { new V2(0, 0), new V2(11, 0) }, 40), "can-fail: an 11-cell shape on a 40-cell cord breaks a target of 40 (51 > 50)");
            Check(CordLayer.OverBudget(40, new List<V2> { new V2(0, 0), new V2(6, 0) }, 40, 2), "the first of two end heaps may take only half the room (6 > 10 / 2)");
            Check(!CordLayer.OverBudget(40, new List<V2> { new V2(0, 0), new V2(4, 0) }, 40, 2), "a heap within half the room fits (4 <= 10 / 2)");
        }
    }
}
