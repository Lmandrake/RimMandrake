using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// CREATURE_JOB_INTERRUPTION_POLICY_1. One interruption rule and one prey rule for the four polling
    /// ambush comps (RM_CompAquaticAmbusher, RM_CompDrumLure, RM_CompHeatBurstPredator,
    /// RM_CompFalseShadeAmbusher), which force jobs with JobCondition.InterruptForced.
    ///
    /// PROVISIONAL (auto-decided 2026-10-09, CREATURE_JOB_INTERRUPTION_POLICY_1):
    ///  - A comp may force a job on a pawn (its own carrier, or a lure victim) only when that pawn is
    ///    spawned, alive, not downed, not in a mental state, not drafted, and not on a player-forced job.
    ///  - Prey is anything the carrier is hostile to, plus (setting ambushWildPreyEnabled, default on)
    ///    factionless animals a WILD predator could hunt by vanilla's own test, FoodUtility.IsAcceptablePreyFor.
    ///    GenHostility never makes wild animals hostile to each other, so HostileTo alone left these
    ///    predators unable to ambush wildlife at all.
    /// </summary>
    public static class RM_AmbushJobPolicy
    {
        public static bool MayForceJobOn(Pawn p)
        {
            if (p == null || !p.Spawned || p.Dead || p.Downed || p.InMentalState || p.Drafted || p.jobs == null)
            {
                return false;
            }
            Job cur = p.jobs.curJob;
            return cur == null || !cur.playerForced;
        }

        public static bool IsPrey(Pawn predator, Pawn candidate)
        {
            if (predator == null || candidate == null || candidate == predator || candidate.Dead || !candidate.Spawned)
            {
                return false;
            }
            if (predator.HostileTo(candidate))
            {
                return true;
            }
            if (!RM_CreatureBehaviorsSettings.ambushWildPreyEnabled)
            {
                return false;
            }
            if (predator.Faction != null || candidate.Faction != null || candidate.def == predator.def
                || !predator.RaceProps.predator || !candidate.RaceProps.Animal)
            {
                return false;
            }
            return FoodUtility.IsAcceptablePreyFor(predator, candidate);
        }
    }
}
