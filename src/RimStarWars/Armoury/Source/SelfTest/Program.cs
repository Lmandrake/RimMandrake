// Armoury offline fuzz entry. Knobs (forwarded by selftest_armoury_fuzz.py): --fuzz-scale F (multiplies every case
// count, 0 skips), --fuzz-seed N (replay one seed of every family), --fuzz-only NAME (ion|yield|gear|kolto|combat).
using System;

namespace RimMandrake.StarWars.Armoury.SelfTest
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            // numbers in failure messages must not print as a locale glyph (an infinity symbol is not UTF-8 on a Windows console)
            System.Globalization.CultureInfo.DefaultThreadCurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
            System.Globalization.CultureInfo.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
            double scale = 1;
            int i = Array.IndexOf(args, "--fuzz-scale");
            if (i >= 0) scale = double.Parse(args[i + 1], System.Globalization.CultureInfo.InvariantCulture);
            int? one = null;
            i = Array.IndexOf(args, "--fuzz-seed");
            if (i >= 0) one = int.Parse(args[i + 1]);
            string only = null;
            i = Array.IndexOf(args, "--fuzz-only");
            if (i >= 0) only = args[i + 1];
            return ArmouryFuzz.Run(scale, one, only) ? 0 : 1;
        }
    }
}
