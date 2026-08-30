using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Spikes
{
    // SPIKE 3 — own the raid math: REPLACE threat points at the single choke point,
    // per the replace-don't-stack ruling (F12) and the Visibility dial (F18).
    //
    // VERIFIED-IN-SOURCE (1.6):
    //   StorytellerUtility.DefaultThreatPointsNow(IIncidentTarget target)
    //     public static float, StorytellerUtility.cs:131 — and it IS the choke
    //     point: ~50 call sites route through it, including
    //     IncidentWorker_RaidEnemy.cs:88 and IncidentWorker_RaidFriendly.cs:69,
    //     quests, sites, Anomaly spawners, ambushes.
    //
    // THE TRICK: one Postfix scaling/replacing __result modulates EVERY threat
    // consumer at once — no per-incident patching. The gods' hands (Ishko down,
    // Ozzik up, Sh'kaar multiplier) and vanilla wealth scaling merge into ONE
    // number here, so nothing double-bills.
    //
    // UNPROVEN UNTIL RUNTIME:
    //   - non-raid consumers (quest sizing, thrumbo herd size at
    //     IncidentWorker_ThrumboPasses, Anomaly curves) also read this — decide
    //     per-consumer whether divine modulation should apply, else a humble
    //     colony gets humble thrumbo herds too. Likely: gate on
    //     target is Map map && map.IsPlayerHome, and accept the rest.
    //   - other mods postfix the same method; ordering via [HarmonyPriority] if a
    //     conflict shows in practice.
    public static class VisibilityStub
    {
        // Placeholder for the F18 Colony Visibility dial (0..1). The real value
        // comes from the Visibility map component when COLONY_VISIBILITY_STAT_1 builds.
        public static float VisibilityFactorFor(IIncidentTarget target) => 1f;
    }

    [HarmonyPatch(typeof(StorytellerUtility), nameof(StorytellerUtility.DefaultThreatPointsNow))]
    public static class Patch_DefaultThreatPointsNow
    {
        public static void Postfix(IIncidentTarget target, ref float __result)
        {
            __result *= VisibilityStub.VisibilityFactorFor(target);
        }
    }
}
