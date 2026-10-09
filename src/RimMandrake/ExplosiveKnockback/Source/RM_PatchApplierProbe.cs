using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>
    /// PATCHAPPLIER_FORCED_MISS_PROBE_1: proves HARMONY_PATCH_RESILIENCE_1.A2 by a state read. Nothing here runs at startup:
    /// the throwaway patch class lives in the ForcedMissProbe sub-namespace, which the mod's own PatchApplier.Apply call
    /// (namespace-filtered to RimMandrake.ExplosiveKnockback) skips. The probe applies it ONCE, on demand, through the real
    /// PatchApplier.Apply, then reports. Read with jawa/static_call type=RimMandrake.ExplosiveKnockback.RM_PatchApplierProbe
    /// method=Probe args="". Side effect: the forced miss stays in this assembly's failure list until the game restarts
    /// (the ExplosiveKnockback Mod Settings page will show it); use a throwaway session.
    /// </summary>
    public static class RM_PatchApplierProbe
    {
        /// <summary>The probe's own switch; PatchApplier flips it to false on the forced miss.</summary>
        public static bool probeFeatureOn = true;

        private static string cached;

        public static string Probe(string unused)
        {
            if (cached != null)
            {
                return cached + " rerun=cached";
            }
            try
            {
                int before = RimMandrake.Shared.PatchApplier.Failures.Count;
                int patched = RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.probe.forcedmiss"),
                    typeof(RM_PatchApplierProbe).Assembly, "RimMandrake.ExplosiveKnockback.ForcedMissProbe",
                    "RimMandrake.ExplosiveKnockback.ForcedMissProbe");
                var failures = RimMandrake.Shared.PatchApplier.Failures;
                int missing = failures.Count - before;
                string feature = missing > 0 ? failures[before].feature : "none";
                cached = "patched=" + patched + " missing=" + missing + " feature=" + feature
                    + " settingOff=" + (!probeFeatureOn)
                    + " isBroken=" + RimMandrake.Shared.PatchApplier.IsBroken("probeFeatureOn")
                    + " totalFailures=" + failures.Count
                    + " logTag=RimMandrake.ExplosiveKnockback.ForcedMissProbe";
                return cached;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }
    }
}

namespace RimMandrake.ExplosiveKnockback.ForcedMissProbe
{
    /// <summary>Deliberately unresolvable: TargetMethod names a method that does not exist, so Harmony throws and
    /// PatchApplier must switch the feature off (and only it). Dynamic target so lint_harmony_targets reports DYNAMIC, not a miss.</summary>
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Forced-miss probe", typeof(RM_PatchApplierProbe), "probeFeatureOn")]
    public static class RM_ForcedMissPatch
    {
        public static MethodBase TargetMethod()
        {
            return typeof(Pawn).GetMethod("RM_NoSuchMethod_ForcedMiss", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static);
        }

        public static void Prefix()
        {
        }
    }
}
