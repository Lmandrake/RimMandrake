// EnvironmentalHazards offline fuzz entry. Knobs (forwarded by selftest_envhazards_fuzz.py): --fuzz-scale F (multiplies
// every case count, 0 skips), --fuzz-seed N (replay one seed of every family), --fuzz-only NAME (axis|quant|pool|prim|cooler|held).
using System;

namespace RimMandrake.EnvironmentalHazards.SelfTest
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
            string[] known = { "axis", "quant", "prim", "pool", "cooler", "held" };
            if (only != null && Array.IndexOf(known, only) < 0) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return 1; }
            bool ok = AxisFuzz.Run(scale, one, only);
            ok &= PoolFuzz.Run(scale, one, only);
            ok &= CoolerFuzz.Run(scale, one, only);
            if (AxisFuzz.Cases + PoolFuzz.Cases + CoolerFuzz.Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return 1; }
            Console.WriteLine(ok ? "ENVHAZARDS FUZZ: PASS" : "ENVHAZARDS FUZZ: FAIL");
            return ok ? 0 : 1;
        }
    }
}
