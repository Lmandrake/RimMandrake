// LeaningScrub offline fuzz entry. Knobs (forwarded by selftest_leaningscrub_fuzz.py): --fuzz-scale F (multiplies every case
// count; a scale that runs no case at all, e.g. 0, FAILS with "no cases ran"), --fuzz-seed N (replay one seed of every family),
// --fuzz-only NAME (lean|smother|blaze|forms|walk|coat; any other name FAILS).
using System;

namespace RimMandrake.LeaningScrub.SelfTest
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
            bool four = LeaningScrubFourFormsCheck.Run();
            bool tonight = LeaningScrubTonightCheck.Run();
            bool islands = LeaningScrubIslandCheck.Run();
            bool plantLean = LeaningScrubPlantLeanCheck.Run();
            bool glide = LeaningScrubGlideCheck.Run();
            return LeaningScrubFuzz.Run(scale, one, only) && four && tonight && islands && plantLean && glide ? 0 : 1;
        }
    }
}
