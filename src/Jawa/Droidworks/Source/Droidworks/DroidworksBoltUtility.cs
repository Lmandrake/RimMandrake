using Verse;

namespace Droidworks
{
    /// <summary>
    /// DROIDWORKS_BOLT_CORE_1 shared helper. Both application routes for
    /// DW_RestrainingBolt - the surgery (Recipe_InstallRestrainingBolt) and
    /// the field clamp (JobDriver_DWClampBolt) - seed DW_BoltResentment
    /// through this one method, so the sapient gate lives in exactly one
    /// place rather than being duplicated at each call site.
    /// </summary>
    public static class DroidworksBoltUtility
    {
        /// <summary>
        /// Adds DW_BoltResentment if the pawn is sapient (Humanlike) and does
        /// not already carry it. Idempotent and safe to call from both bolt
        /// application routes unconditionally.
        /// </summary>
        public static void EnsureBoltResentment(Pawn pawn)
        {
            if (pawn?.health?.hediffSet == null) return;
            if (pawn.RaceProps == null || pawn.RaceProps.intelligence != Intelligence.Humanlike) return;
            if (pawn.health.hediffSet.HasHediff(DroidworksDefOf.DW_BoltResentment)) return;
            pawn.health.AddHediff(DroidworksDefOf.DW_BoltResentment);
        }
    }
}
