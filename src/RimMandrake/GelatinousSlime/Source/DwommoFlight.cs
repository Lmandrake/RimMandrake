using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_DWOMMO_FLIER_1: flight in 1.6 is a STAT (Pawn_FlightTracker.CanEverFly reads
    // MaxFlightTime > 0), so the Mod Settings switch edits that stat on the loaded def. Off =>
    // MaxFlightTime 0, the dwommo stays on the map but never takes off. On restores the shipped value.
    // Stat caches may keep a stale value on pawns already spawned until they are reloaded.
    [StaticConstructorOnStartup]
    public static class DwommoFlight
    {
        const float ShippedMaxFlightTime = 60f;

        static DwommoFlight()
        {
            Apply();
        }

        public static void Apply()
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Dwommo");
            if (def == null || def.statBases == null) return;
            float want = SlimeSettings.dwommoFlies ? ShippedMaxFlightTime : 0f;
            for (int i = 0; i < def.statBases.Count; i++)
            {
                if (def.statBases[i].stat == StatDefOf.MaxFlightTime)
                {
                    def.statBases[i].value = want;
                    return;
                }
            }
        }
    }
}
