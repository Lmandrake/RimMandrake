using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_BREAKTHROUGH_CLEARING_1: the one hook. Pawn_PathFollower.StartPath (decompiled 1.6) is where a sealed destination
    /// fails (Reachability.CanReach(PassDoors) false, then PatherFailed) before any step is taken, so this is the only place a
    /// titan can be turned toward the obstacle instead. When TitanClearingUtility starts a clearing job the original StartPath is
    /// skipped (the job it belonged to is suspended and resumes afterwards); otherwise vanilla runs unchanged.
    /// Ending and starting jobs from inside StartPath is the engine's own pattern: PatherFailed ends the job from right here.
    /// Cost when off: one static read. On: a comp lookup per path start for an untiered pawn.
    /// </summary>
    [HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.StartPath))]
    internal static class Patch_StartPath_TitanClearing
    {
        private static bool Prefix(Pawn ___pawn, LocalTargetInfo dest, PathEndMode peMode)
        {
            if (!RimMandrake.HugeThings.RM_HugeThingsSettings.TitanClearingActive) return true;
            if (___pawn == null || ___pawn.TryGetComp<CompTitanicWake>() == null) return true;
            return !TitanClearingUtility.TryStartClearing(___pawn, dest, peMode);
        }
    }
}
