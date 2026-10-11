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

        // ---- Phase 2: one mood per map, groups. A consumer supplies rank; Phase 2 carries it and orders nothing.
        // Group names: a registered group, or one of the framework's own "ship" / "rooms" / "halls" / "exterior".

        public static bool PushMood(Map map, string claimant, string group, RM_AtmosphericSchemeDef scheme, float rank = 0f)
        {
            RM_MapComponent_AtmosphericBase c = RM_MapComponent_AtmosphericBase.For(map);
            return c != null && c.PushMood(claimant, group, scheme, rank, out _);
        }

        public static bool ReleaseMood(Map map, string claimant) => RM_MapComponent_AtmosphericBase.For(map)?.ReleaseMood(claimant) ?? false;
        public static RM_MoodClaim CurrentMood(Map map) => RM_MapComponent_AtmosphericBase.For(map)?.EffectiveMood;
        public static void RegisterGroup(Map map, string name, IEnumerable<Thing> members) => RM_MapComponent_AtmosphericBase.For(map)?.RegisterGroup(name, members);
        public static bool UnregisterGroup(Map map, string name) => RM_MapComponent_AtmosphericBase.For(map)?.UnregisterGroup(name) ?? false;

        /// <summary>What the compositor last wrote to this fixture: "substrate" (its own glow), "scheme:index", or null
        /// when it is not held or has not been evaluated yet.</summary>
        public static string Showing(Thing t)
        {
            RM_MapComponent_AtmosphericBase c = RM_MapComponent_AtmosphericBase.For(t?.MapHeld);
            if (c == null || !c.IsTaken(t) || !c.compositor.Shows(t, out long v)) return null;
            if (v == RM_ChangeTracker.Substrate) return "substrate";
            ushort hash = (ushort)(v >> 8);
            RM_AtmosphericSchemeDef d = DefDatabase<RM_AtmosphericSchemeDef>.AllDefsListForReading.Find(x => x.shortHash == hash);
            return (d?.defName ?? "?") + ":" + (v & 0xFF);
        }

        public static void SetScenarioDecides(Map map, bool decides)
        {
            RM_MapComponent_AtmosphericBase c = RM_MapComponent_AtmosphericBase.For(map);
            if (c != null) c.scenarioDecides = decides;
        }
    }
}
