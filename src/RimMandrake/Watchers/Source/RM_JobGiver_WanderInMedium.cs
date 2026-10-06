using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, design §3/§4: the medium lock's wander half, the
    /// RM_JobGiver_WanderInShadeGrid shape (a JobGiver_Wander whose wanderDestValidator only offers
    /// medium cells), at the same Animal_PreWander insert, after the watch. Off its medium it walks
    /// back to the nearest medium cell first. A member whose medium is IsWater (our deep sand) also
    /// sets race waterSeeker, without which vanilla wander refuses avoidWander terrain at all
    /// (RCellFinder; design §1).
    /// </summary>
    public class RM_JobGiver_WanderInMedium : JobGiver_Wander
    {
        public RM_JobGiver_WanderInMedium()
        {
            wanderRadius = 6f;
            ticksBetweenWandersRange = new IntRange(300, 900);
            expiryInterval = 500;
            wanderDestValidator = ValidateWanderDest;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_WatcherExtension ext = pawn?.def.GetModExtension<RM_WatcherExtension>();
            if (ext == null || !ext.HasMedium || !RM_WatchersSettings.watchersEnabled || !RM_WatchersSettings.stayOnMedium
                || pawn.Map == null)
            {
                return null;
            }
            RM_CompWatcher comp = pawn.GetComp<RM_CompWatcher>();
            if (comp != null && comp.NoMediumReachable)
            {
                return null;
            }
            if (!RM_WatcherUtility.OnMedium(pawn, ext))
            {
                if (RM_WatcherUtility.TryFindMediumCell(pawn, ext, out IntVec3 cell))
                {
                    Job go = JobMaker.MakeJob(RM_WatchersDefOf.RM_WatcherRelocate, cell);
                    go.locomotionUrgency = LocomotionUrgency.Walk;
                    return go;
                }
                if (comp != null)
                {
                    comp.noMediumUntilTick = Find.TickManager.TicksGame + 7500;
                }
                return null;
            }
            return base.TryGiveJob(pawn);
        }

        protected override IntVec3 GetWanderRoot(Pawn pawn)
        {
            return pawn.Position;
        }

        private static bool ValidateWanderDest(Pawn pawn, IntVec3 cell, IntVec3 root)
        {
            RM_WatcherExtension ext = pawn.def.GetModExtension<RM_WatcherExtension>();
            return ext != null && pawn.Map != null && ext.IsMedium(cell.GetTerrain(pawn.Map));
        }
    }
}
