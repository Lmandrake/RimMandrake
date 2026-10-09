// Huge Things offline fuzz entry: the plant half (HugeThingsFuzz), the titan half (TitanicFuzz, merged from Titanic Creatures
// 2026-10-07) and the seam between them (HugeTitanFuzz). Knobs (forwarded by selftest_hugethings_fuzz.py): --fuzz-scale F
// (multiplies every case count; must be > 0), --fuzz-seed N (replay one seed of every family), --fuzz-only NAME, where NAME is
// any|full|boundary|symmetry|ledger|planner|items|root|cache|damage|hitbox|determinism (plants), tier|yield|crush|pool (titans) or
// smash|smashstep|gates|titandeterminism (the seam).
using System;
using System.Linq;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class Program
    {
        private static readonly string[] PlantFamilies =
            { "any", "full", "boundary", "symmetry", "ledger", "planner", "items", "root", "cache", "damage", "hitbox", "determinism" };
        private static readonly string[] TitanFamilies = { "tier", "yield", "crush", "pool" };

        private static int Main(string[] args)
        {
            double scale = 1;
            int i = Array.IndexOf(args, "--fuzz-scale");
            if (i >= 0) scale = double.Parse(args[i + 1], System.Globalization.CultureInfo.InvariantCulture);
            // HUGETHINGS_TEST_HONESTY_1 (C3.8): a scale of zero or less ran no cases and printed ALL PASS. Refused centrally.
            if (!(scale > 0) || double.IsInfinity(scale))
            {
                Console.WriteLine("FAIL --fuzz-scale must be a finite number > 0 (got " + scale + "): a fuzz that runs nothing is not a pass");
                return 1;
            }
            int? one = null;
            i = Array.IndexOf(args, "--fuzz-seed");
            if (i >= 0) one = int.Parse(args[i + 1]);
            string only = null;
            i = Array.IndexOf(args, "--fuzz-only");
            if (i >= 0) only = args[i + 1];
            if (only != null && !PlantFamilies.Contains(only) && !TitanFamilies.Contains(only) && !HugeTitanFuzz.Families.Contains(only))
            {
                Console.WriteLine("FAIL unknown --fuzz-only family: " + only);
                return 1;
            }
            bool ok = true;
            if (only == null || PlantFamilies.Contains(only)) ok &= HugeThingsFuzz.Run(scale, one, only);
            if (only == null || TitanFamilies.Contains(only)) ok &= RimMandrake.TitanicCreatures.SelfTest.TitanicFuzz.Run(scale, one, only);
            if (only == null || HugeTitanFuzz.Families.Contains(only)) ok &= HugeTitanFuzz.Run(scale, one, only);
            long total = HugeThingsFuzz.Cases + RimMandrake.TitanicCreatures.SelfTest.TitanicFuzz.Cases + HugeTitanFuzz.Cases;
            if (total == 0)
            {
                Console.WriteLine("FAIL no fuzz case ran at all: a fuzz that checked nothing is not a pass");
                ok = false;
            }
            Console.WriteLine(ok ? "HUGE THINGS FUZZ: ALL PASS" : "HUGE THINGS FUZZ: FAILURES");
            return ok ? 0 : 1;
        }
    }
}
