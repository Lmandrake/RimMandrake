// WreckedMachines offline fuzz entry. Knobs (forwarded by selftest_wreckedmachines_fuzz.py): --fuzz-scale F (multiplies every case count;
// a scale that runs 0 cases FAILS, a fuzz that checked nothing is not a pass), --fuzz-seed N (replay one seed of every family),
// --fuzz-only NAME (ladder|place|emanator|scale|salvage).
// --walk runs the repair state walk instead (RepairWalk.cs; selftest_wreckedmachines_repair_walk.py): --walk-scale F multiplies the count
// of random event strings, --walk-seed N replays one string, --walk-table PATH writes the table of states by events.
using System;

namespace RimMandrake.WreckedMachines.SelfTest
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            if (Array.IndexOf(args, "--walk") >= 0)
            {
                double ws = 1;
                int w = Array.IndexOf(args, "--walk-scale");
                if (w >= 0) ws = double.Parse(args[w + 1], System.Globalization.CultureInfo.InvariantCulture);
                int? seed = null;
                w = Array.IndexOf(args, "--walk-seed");
                if (w >= 0) seed = int.Parse(args[w + 1]);
                w = Array.IndexOf(args, "--walk-table");
                try { return RepairWalk.Run(ws, seed, w >= 0 ? args[w + 1] : null) ? 0 : 1; }
                catch (Exception ex)
                {
                    // a kernel so wrong that the fake game cannot go on is a FAIL with its cause, never a bare crash code
                    Console.WriteLine("FAIL the walk threw: " + ex.GetType().Name + ": " + ex.Message);
                    Console.WriteLine("T_REPAIR_STATE_WALK: FAIL");
                    return 1;
                }
            }
            double scale = 1;
            int i = Array.IndexOf(args, "--fuzz-scale");
            if (i >= 0) scale = double.Parse(args[i + 1], System.Globalization.CultureInfo.InvariantCulture);
            int? one = null;
            i = Array.IndexOf(args, "--fuzz-seed");
            if (i >= 0) one = int.Parse(args[i + 1]);
            string only = null;
            i = Array.IndexOf(args, "--fuzz-only");
            if (i >= 0) only = args[i + 1];
            return WreckedFuzz.Run(scale, one, only) ? 0 : 1;
        }
    }
}
