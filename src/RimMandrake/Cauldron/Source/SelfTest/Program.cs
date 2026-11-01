// Cauldron offline fuzz entry. Knobs (forwarded by selftest_cauldron_fuzz.py): --fuzz-scale F (multiplies every case count,
// 0 skips), --fuzz-seed N (replay one seed of every family), --fuzz-only NAME (vent|yield|prints|units).
using System;

namespace RimMandrake.Cauldron.SelfTest
{
    internal static class Program
    {
        // VEXXITH_USES_1: the ambient-acid rules, on the production kernel.
        private static bool AcidAirChecks()
        {
            var fails = new System.Collections.Generic.List<string>();
            Action<bool, string> ok = (c, m) => { if (!c) fails.Add(m); };
            ok(RM_AcidAirKernel.BurnChance(1f, 0f, 0f) == RM_AcidAirKernel.PawnBurnChance, "an unsealed pawn burns at the base chance");
            ok(RM_AcidAirKernel.BurnChance(1f, 1.01f, 0.8f) == 0f, "vacsuit and helmet (1.01) seal fully");
            float body = RM_AcidAirKernel.BurnChance(1f, 0.32f, 0f);
            ok(body > 0f && body < RM_AcidAirKernel.PawnBurnChance, "a suit without its helmet only partly seals");
            ok(RM_AcidAirKernel.BurnChance(2f, 0f, 0f) == 2f * RM_AcidAirKernel.PawnBurnChance, "the factor scales the chance");
            ok(RM_AcidAirKernel.PawnExposed(false, true, false, false, false, false), "a raider or colonist under open sky is exposed");
            ok(!RM_AcidAirKernel.PawnExposed(false, true, false, true, false, false), "roofed ground is out of the air");
            ok(!RM_AcidAirKernel.PawnExposed(false, true, false, false, true, true), "a native animal is used to it");
            ok(RM_AcidAirKernel.PawnExposed(false, true, false, false, true, false), "a foreign animal burns");
            ok(RM_AcidAirKernel.HullBurns(true, false, true, true, 100, 100), "an exposed ship building burns");
            ok(!RM_AcidAirKernel.HullBurns(true, true, true, true, 100, 100), "a lined ship does not");
            ok(!RM_AcidAirKernel.HullBurns(false, false, true, true, 100, 100), "the toggle stops it");
            ok(!RM_AcidAirKernel.HullBurns(true, false, false, true, 100, 100), "off the ship nothing burns");
            ok(!RM_AcidAirKernel.HullBurns(true, false, true, false, 100, 100), "a sheltered ship part does not burn");
            ok(!RM_AcidAirKernel.HullBurns(true, false, true, true, 30, 100), "it stops at the 30% floor");
            ok(RM_AcidAirKernel.HullBurns(true, false, true, true, 31, 100), "just above the floor it still burns");
            foreach (string f in fails) Console.WriteLine("FAIL acid air: " + f);
            return fails.Count == 0;
        }

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
            return AcidAirChecks() && CauldronFuzz.Run(scale, one, only) ? 0 : 1;
        }
    }
}
