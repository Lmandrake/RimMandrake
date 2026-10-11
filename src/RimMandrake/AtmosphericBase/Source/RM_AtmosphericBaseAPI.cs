// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- the code door, as far as Phase 1 reaches (spec §2.8). A scenario that
// decides for a map calls SetScenarioDecides(map, true) and then TakeOver for the fixtures it hands over; the player's
// buttons are hidden on that map. Groups, moods and gestures are later phases.
using System.Collections.Generic;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public static class RM_AtmosphericBaseAPI
    {
        public static bool IsEligible(Thing t) => RM_EmitterDiscovery.Classify(t) == RM_EmitterVerdict.Eligible;
        public static IEnumerable<Building> DiscoverEmitters(Map map) => RM_EmitterDiscovery.EligibleOn(map);
        public static bool TakeOver(Thing t) => RM_MapComponent_AtmosphericBase.For(t?.MapHeld)?.TakeOver(t) ?? false;
        public static bool Release(Thing t) => RM_MapComponent_AtmosphericBase.For(t?.MapHeld)?.Release(t) ?? false;
        public static bool IsTaken(Thing t) => RM_MapComponent_AtmosphericBase.For(t?.MapHeld)?.IsTaken(t) ?? false;
        public static int ReleaseAll(Map map) => RM_MapComponent_AtmosphericBase.For(map)?.ReleaseAll() ?? 0;

        public static void SetScenarioDecides(Map map, bool decides)
        {
            RM_MapComponent_AtmosphericBase c = RM_MapComponent_AtmosphericBase.For(map);
            if (c != null) c.scenarioDecides = decides;
        }
    }
}
