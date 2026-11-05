// GSS_CORD_LOOPS_FIX_SPREAD_INTO_DOORS (GPT review FB_hose_gss_3.4, 2026-10-23): AddLoops' ordinary loop/heap branch checked
// AllClear, length and Lassoes but never doors, so a loop rooted beside a doorway could spread into it (design 8: "no loops or
// heaps in the doorway"; the end-heap branch already refused door points). Scene: a straight strand along z = 5.5 with a door
// row on each side (z = 4 and z = 6). Can-fail: the same lays with plain floor there DO reach those rows.
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class DoorLoopChecks
    {
        // the harness prints only failures; these rows also print their verdict, so a reader of the run sees them hold
        private static void Check(bool ok, string msg)
        {
            System.Console.WriteLine((ok ? "PASS" : "FAIL") + " door-loop: " + msg);
            Program.Check(ok, "door-loop: " + msg);
        }

        private static CordWorld Scene(bool doors)
        {
            var w = new CordWorld(24, 12);
            if (doors)
            {
                for (int x = 0; x < 24; x++)
                {
                    w.SetDoor(new Cell(x, 4));
                    w.SetDoor(new Cell(x, 6));
                }
            }
            return w;
        }

        private static int OnDoorRows(List<V2> q)
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
                foreach (bool doors in new[] { false, true })
                {
                    var Q = new List<V2>();
                    for (double x = 2; x <= 20.0001; x += 0.05) Q.Add(new V2(x, 5.5));
                    var ramp = new double[Q.Count];
                    for (int i = 0; i < ramp.Length; i++) ramp[i] = 1;
                    int before = Q.Count;
                    List<V2> o = CordLayer.AddLoops(Scene(doors), Q, ramp, prm, CordRng.Of(seed, "doorloop"), 200, new SettleStats());
                    if (doors) { hitWith += OnDoorRows(o); if (o.Count > before) loopsWith++; }
                    else hitWithout += OnDoorRows(o);
                }
            }
            Check(hitWithout > 0, $"can-fail: with plain floor there the loops reach those cells ({hitWithout} points)");
            Check(hitWith == 0, $"no loop or heap point lies in a doorway the strand does not run through ({hitWith} points)");
            Check(loopsWith > 0, $"loops still form, small enough to stay out of the doorways ({loopsWith}/40 lays)");
        }
    }
}
