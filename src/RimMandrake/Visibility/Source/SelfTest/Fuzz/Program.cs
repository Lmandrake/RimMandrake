// Visibility offline fuzz entry. Knobs: --fuzz-scale F (multiplies every case count, 0 skips), --fuzz-seed N (replay one seed of every
// family), --fuzz-only NAME (band|curve|dial|memory|points).
using System;

namespace RimMandrake.Visibility.SelfTest
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            double scale = 1;
            int i = Array.IndexOf(args, "--fuzz-scale");
            if (i >= 0) scale = double.Parse(args[i + 1], System.Globalization.CultureInfo.InvariantCulture);
            int? one = null;
            i = Array.IndexOf(args, "--fuzz-seed");
            if (i >= 0) one = int.Parse(args[i + 1]);
            string only = null;
            i = Array.IndexOf(args, "--fuzz-only");
            if (i >= 0) only = args[i + 1];
            return VisibilityFuzz.Run(scale, one, only) ? 0 : 1;
        }
    }
}
