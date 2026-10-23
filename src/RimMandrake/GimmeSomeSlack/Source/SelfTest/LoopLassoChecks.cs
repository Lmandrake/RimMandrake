// CORD_LOOP_UNTANGLE_LASSOED_A_PIPE (BENCH live round 3a, 2026-10-23, map R C1): a canned slack loop was spliced round the
// water pipe beside a battery-to-pump cord and read as a tangle. Scene: a straight strand along z = 5.5 with a pipe row on
// each side (z = 4 and z = 6, busy). Can-fail: the same lays with no busy cells DO reach the pipe rows.
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LoopLassoChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "loop-lasso: " + msg);

        private static CordWorld Scene(bool pipes)
        {
            var w = new CordWorld(24, 12);
            if (pipes)
            {
                for (int x = 0; x < 24; x++)
                {
                    w.SetBusy(new Cell(x, 4));
                    w.SetBusy(new Cell(x, 6));
                }
            }
            return w;
        }

        private static int OnPipeRows(List<V2> q)
        {
            int n = 0;
            foreach (V2 p in q)
            {
                int z = p.Floor.Z;
                if (z == 4 || z == 6) n++;
            }
            return n;
        }

        public static void Run()
        {
            var prm = new LayParams { LoopsPerCell = 0.6, HeapP = 1.0 };
            int hitWithout = 0, hitWith = 0, loopsWith = 0;
            for (int seed = 1; seed <= 40; seed++)
            {
                foreach (bool pipes in new[] { false, true })
                {
                    var Q = new List<V2>();
                    for (double x = 2; x <= 20.0001; x += 0.05) Q.Add(new V2(x, 5.5));
                    var ramp = new double[Q.Count];
                    for (int i = 0; i < ramp.Length; i++) ramp[i] = 1;
                    int before = Q.Count;
                    List<V2> o = CordLayer.AddLoops(Scene(pipes), Q, ramp, prm, CordRng.Of(seed, "lasso"), 200, new SettleStats());
                    if (pipes) { hitWith += OnPipeRows(o); if (o.Count > before) loopsWith++; }
                    else hitWithout += OnPipeRows(o);
                }
            }
            Check(hitWithout > 0, $"can-fail: with no busy cells the loops reach the pipe rows ({hitWithout} points)");
            Check(hitWith == 0, $"no loop or heap point lies on a pipe row the strand does not run through ({hitWith} points)");
            Check(loopsWith > 0, $"loops still form, small enough to stay in the strand's own row ({loopsWith}/40 lays)");

            // a busy cell the strand already runs through (its own conduit, a pipe it crosses) does not refuse a loop
            var w = new CordWorld(8, 8);
            w.SetBusy(new Cell(3, 3));
            Check(!CordLayer.Lassoes(w, new List<V2> { new V2(3.4, 3.6) }, new HashSet<Cell> { new Cell(3, 3) }), "the strand's own busy cell is allowed");
            Check(CordLayer.Lassoes(w, new List<V2> { new V2(3.4, 3.6) }, new HashSet<Cell> { new Cell(2, 3) }), "can-fail: a busy cell off the strand refuses the shape");
            Check(!CordLayer.Lassoes(new CordWorld(8, 8), new List<V2> { new V2(3.4, 3.6) }, null), "no busy cells: nothing refused");
        }
    }
}
