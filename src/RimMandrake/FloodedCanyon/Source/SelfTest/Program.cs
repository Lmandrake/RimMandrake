// FloodedCanyon offline fuzz entry. Knobs (forwarded by selftest_floodedcanyon_fuzz.py): --fuzz-scale F (multiplies every case
// count, 0 skips), --fuzz-seed N (replay one seed of every family), --fuzz-only NAME (flood|cells|refuge|pan|rules).
using System;

namespace RimMandrake.FloodedCanyon.SelfTest
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            // CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1: the dust kernel drifts forward, reverses fully and briefly, and is inert when off.
            {
                int rev = 0; float min = 1f;
                for (long t = 0; t < RM_DustKernel.PeriodTicks * 3; t++)
                {
                    float f = RM_DustKernel.Factor(t, true);
                    if (f < 0f) rev++;
                    if (f < min) min = f;
                    if (RM_DustKernel.Factor(t, false) != 1f) { Console.Error.WriteLine("dust kernel not inert when off"); return 1; }
                }
                if (min != -1f || rev == 0 || rev >= RM_DustKernel.ReverseTicks * 3 || RM_DustKernel.Factor(0, true) != 1f)
                { Console.Error.WriteLine("dust kernel reversal wrong: min=" + min + " rev=" + rev); return 1; }
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
            return FloodedCanyonFuzz.Run(scale, one, only) ? 0 : 1;
        }
    }
}
