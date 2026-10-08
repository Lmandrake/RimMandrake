// StructureInjections offline fuzz entry. Knobs (forwarded by selftest_structureinjections_fuzz.py): --fuzz-scale F, --fuzz-seed N,
// --fuzz-only NAME (parse|malformed|offset|run|order|tables|templates), --plans <dir> (the shipped Templates folder).
using System;

namespace RimMandrake.StructureInjections.SelfTest
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
            string plans = null;
            i = Array.IndexOf(args, "--plans");
            if (i >= 0) plans = args[i + 1];
            return StructureInjectionsFuzz.Run(scale, one, only, plans) ? 0 : 1;
        }
    }
}
