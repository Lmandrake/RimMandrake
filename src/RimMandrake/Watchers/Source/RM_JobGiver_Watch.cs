using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, design §3. Inserted at Core's Animal_PreWander (RM_Watchers think
    /// tree), so hunger, sleep, fleeing and taming above it in Core's tree still win; its first
    /// statement rejects every race without RM_WatcherExtension, so the global insert costs other
    /// animals nothing (the RM_JobGiver_BurrowOnFire shape).
    /// </summary>
    public class RM_JobGiver_Watch : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_WatcherExtension ext = pawn?.def.GetModExtension<RM_WatcherExtension>();
            if (ext == null || !RM_WatchersSettings.watchersEnabled)
            {
                return null;
            }
            if (!pawn.Spawned || pawn.Downed || pawn.InMentalState || pawn.Map == null)
            {
                return null;
            }
            RM_CompWatcher comp = pawn.GetComp<RM_CompWatcher>();
            // Below the emerge threshold the job would hide then end at once (hungry), and this giver
            // would re-issue it: a hide/emerge loop every ~60 ticks whenever food is out of reach.
            // It only ever watches (and so only ever hides) on its medium.
            if (!RM_WatcherKernel.WatchGiverPre(true, RM_WatchersSettings.watchersEnabled, true, false, false, true,
                    comp != null, comp != null && comp.Bolting, RM_WatcherUtility.OnMedium(pawn, ext),
                    RM_WatchersSettings.hideAndFlinch, RM_WatchersSettings.turnToFace,
                    pawn.needs?.food != null, pawn.needs?.food != null ? pawn.needs.food.CurLevelPercentage : 1f,
                    ext.emergeWhenFoodBelow))
            {
                return null;
            }
            // The roll first: the map-wide scan only runs for an animal that did not just decide to wander.
            if (Rand.Chance(ext.wanderChance)
                || !RM_WatcherKernel.WatchGiverCapOk(false, RM_WatcherUtility.ActiveWatchers(pawn.Map), RM_WatchersSettings.maxActivePerMap))
            {
                return null;
            }
            return JobMaker.MakeJob(RM_WatchersDefOf.RM_WatcherWatch);
        }
    }
}
