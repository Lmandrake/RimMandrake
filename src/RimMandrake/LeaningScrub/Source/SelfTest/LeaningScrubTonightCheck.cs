using System;

namespace RimMandrake.LeaningScrub.SelfTest
{
    // LEANINGSCRUB_MECHANICS_BUILD_1 parts 5b/6/8: table checks of the ripple, calling-pyre and injection kernels.
    internal static class LeaningScrubTonightCheck
    {
        public static bool Run()
        {
            int bad = 0;
            void Eq(string n, object got, object want) { if (!Equals(got, want)) { bad++; Console.Error.WriteLine("FAIL " + n + " " + got + " != " + want); } }
            // ripple
            Eq("hare hides in wind", RM_RippleKernel.Hidden(true, true, false, true, 0.2f, 0.6f, false, false, true), true);
            Eq("off hides nobody", RM_RippleKernel.Hidden(false, true, false, true, 0.2f, 0.6f, false, false, false), false);
            Eq("tame never hides", RM_RippleKernel.Hidden(true, false, false, true, 0.2f, 0.6f, false, false, false), false);
            Eq("bare ground no cover", RM_RippleKernel.Hidden(true, true, false, false, 0.2f, 0.6f, false, false, false), false);
            Eq("downed shown", RM_RippleKernel.Hidden(true, true, true, true, 0.2f, 0.6f, false, false, false), false);
            Eq("too big in wind", RM_RippleKernel.Hidden(true, true, false, true, 1.0f, 0.6f, false, false, false), false);
            Eq("gale doubles size", RM_RippleKernel.Hidden(true, true, false, true, 1.0f, 0.6f, true, false, true), true);
            Eq("stall mover seen", RM_RippleKernel.Hidden(true, true, false, true, 0.2f, 0.6f, false, true, true), false);
            Eq("stall still hidden", RM_RippleKernel.Hidden(true, true, false, true, 0.2f, 0.6f, false, true, false), true);
            Eq("negative limit", RM_RippleKernel.SizeLimit(-1f, true), 0f);
            // stall hunt
            Eq("hunts in stall", RM_StallHuntKernel.Hunts(true, true, true, true, false, false, false), true);
            Eq("idle in wind", RM_StallHuntKernel.Hunts(true, false, true, true, false, false, false), false);
            Eq("off idle", RM_StallHuntKernel.Hunts(false, true, true, true, false, false, false), false);
            Eq("tame idle", RM_StallHuntKernel.Hunts(true, true, false, true, false, false, false), false);
            Eq("already hunting", RM_StallHuntKernel.Hunts(true, true, true, true, false, false, true), false);
            Eq("hidden prey safe", RM_StallHuntKernel.Prey(true, false, false, true, 0.2f, 0.65f), false);
            Eq("visible prey taken", RM_StallHuntKernel.Prey(true, false, false, false, 0.2f, 0.65f), true);
            Eq("own kind safe", RM_StallHuntKernel.Prey(true, true, false, false, 0.2f, 0.65f), false);
            Eq("big prey safe", RM_StallHuntKernel.Prey(true, false, false, false, 1.0f, 0.65f), false);
            // pyre gate
            Eq("off refuses", RM_PyreKernel.Gate(false, RM_PyreKernel.BeliefVenerated, 1), RM_PyreKernel.ReasonOff);
            Eq("forbidden refuses", RM_PyreKernel.Gate(true, RM_PyreKernel.BeliefForbidden, 5), RM_PyreKernel.ReasonForbidden);
            Eq("last rite needs enemies", RM_PyreKernel.Gate(true, RM_PyreKernel.BeliefLastRite, 0), RM_PyreKernel.ReasonNoEnemies);
            Eq("last rite with enemies", RM_PyreKernel.Gate(true, RM_PyreKernel.BeliefLastRite, 2), RM_PyreKernel.Ok);
            Eq("venerated any time", RM_PyreKernel.Gate(true, RM_PyreKernel.BeliefVenerated, 0), RM_PyreKernel.Ok);
            Eq("no belief refuses", RM_PyreKernel.Gate(true, RM_PyreKernel.BeliefNone, 3), RM_PyreKernel.ReasonNoBelief);
            for (int tier = -2; tier < 7; tier++)
            {
                if (RM_PyreKernel.FireCount(tier) < 5) { bad++; Console.Error.WriteLine("FAIL fire tier " + tier + " under stamp threshold"); }
                for (float f = 0f; f <= 3f; f += 0.5f)
                {
                    int h = RM_PyreKernel.HerdCount(tier, f);
                    int r = RM_PyreKernel.RagingCount(tier, h);
                    if (h < 0 || h > 40 || r < 0 || r > h) { bad++; Console.Error.WriteLine("FAIL herd " + tier + "/" + f + " h=" + h + " r=" + r); }
                    if (f > 0f && h < 1) { bad++; Console.Error.WriteLine("FAIL herd vanished at factor " + f); }
                }
            }
            Eq("zero factor zero herd", RM_PyreKernel.HerdCount(2, 0f), 0);
            Eq("NaN factor zero herd", RM_PyreKernel.HerdCount(2, float.NaN), 0);
            Eq("terrible all rage", RM_PyreKernel.RagingCount(0, 4), 4);
            Eq("great quarter rage", RM_PyreKernel.RagingCount(3, 8), 2);
            Eq("worse rite more rage", RM_PyreKernel.RagingCount(1, 6) >= RM_PyreKernel.RagingCount(2, 6), true);
            // injections
            Eq("first ruin farmstead", RM_InjectionKernel.RuinKind(0, 0.99), RM_InjectionKernel.RuinFarmstead);
            Eq("later low roll smother", RM_InjectionKernel.RuinKind(2, 0.1), RM_InjectionKernel.RuinSmotherField);
            Eq("later high roll hedge", RM_InjectionKernel.RuinKind(1, 0.9), RM_InjectionKernel.RuinHedgeHomestead);
            Eq("hp floor", RM_InjectionKernel.RuinHitPoints(300, 0.0), 75);
            Eq("hp top", RM_InjectionKernel.RuinHitPoints(300, 1.0), 180);
            Eq("hp tiny", RM_InjectionKernel.RuinHitPoints(0, 0.5), 1);
            Eq("near centre refused", RM_InjectionKernel.Spaced(130, 130, new int[0], new int[0], 0, 32f, 125, 125, 36f), false);
            Eq("spaced ok", RM_InjectionKernel.Spaced(30, 30, new[] { 100 }, new[] { 100 }, 1, 32f, 125, 125, 36f), true);
            Eq("too close to placed", RM_InjectionKernel.Spaced(30, 30, new[] { 40 }, new[] { 40 }, 1, 32f, 125, 125, 36f), false);
            Eq("mid-cycle never negative", RM_InjectionKernel.MidCycleStart(100, 1800000, 0.5), 0);
            Eq("mid-cycle back 50%", RM_InjectionKernel.MidCycleStart(2000000, 1000000, 0.5), 1500000);
            Console.WriteLine(bad == 0 ? "tonight check: ok" : "tonight check: " + bad + " FAILED");
            return bad == 0;
        }
    }
}
