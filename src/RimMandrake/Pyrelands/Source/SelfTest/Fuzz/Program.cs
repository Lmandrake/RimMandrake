// Pyrelands offline fuzz entry. Knobs (forwarded by selftest_pyrelands_fuzz.py): --fuzz-scale F (multiplies every case count, 0 skips),
// --fuzz-seed N (replay one seed of every family), --fuzz-only NAME (burn|furnace|breaker|eco|units), --tuning <path to PyrelandsTuning.cs>.
using System;

namespace RimMandrake.Pyrelands.Fuzz
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
            string tuning = null;
            i = Array.IndexOf(args, "--tuning");
            if (i >= 0) tuning = args[i + 1];
            return PyrelandsFuzz.Run(scale, one, only, tuning) ? 0 : 1;
        }
    }
}
