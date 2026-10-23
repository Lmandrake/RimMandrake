// Ninefold fuzz entry. Knobs (forwarded by selftest_ninefold_fuzz.py): --fuzz-scale F, --fuzz-seed N (replay one
// seed of every family), --fuzz-only seq|band|rank|mood.
// --legacy-map NAME... prints "NAME<TAB>MAPPED" per name through the production save type alias
// (NinefoldLegacyTypesKernel.MapTypeName; "-" when the name is not mapped) and exits; no fuzz runs.
using System;

namespace RimMandrake.Utinni.Rites.SelfTest
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            int lm = Array.IndexOf(args, "--legacy-map");
            if (lm >= 0)
            {
                for (int k = lm + 1; k < args.Length; k++)
                    Console.WriteLine(args[k] + "\t" + (NinefoldLegacyTypesKernel.MapTypeName(args[k]) ?? "-"));
                return 0;
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
            return NinefoldFuzz.Run(scale, one, only) ? 0 : 1;
        }
    }
}
