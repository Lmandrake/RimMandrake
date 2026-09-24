using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// BACTA_REVIVAL_MECHANIC_1. Scans loose corpses for one a bacta tank can still revive and
    /// carries it there — the mirror image of WorkGiver_CarryToBactaTank, which scans the
    /// BUILDING for a selection a living pawn already made. A corpse can't select anything for
    /// itself, so this scans corpses directly, the same shape vanilla's WorkGiver_HaulCorpses
    /// uses for burial (ThingRequestGroup.Corpse, one JobOnThing per corpse found).
    /// </summary>
    public class WorkGiver_CarryCorpseToBactaTank : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup(ThingRequestGroup.Corpse);

        public override PathEndMode PathEndMode => PathEndMode.OnCell;

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            // Cheap global gate before any per-corpse scan: revival off means nothing here is
            // ever workable, so don't pay for a corpse scan at all.
            return !BactaSettings.revivalEnabled;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!(t is Corpse corpse))
            {
                return false;
            }
            if (!pawn.CanReserveAndReach(corpse, PathEndMode.OnCell, Danger.Deadly, 1, -1, null, forced))
            {
                return false;
            }
            if (corpse.IsForbidden(pawn))
            {
                return false;
            }
            return FindTank(pawn, corpse) != null;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Corpse corpse = (Corpse)t;
            Building_BactaTank tank = FindTank(pawn, corpse);
            if (tank == null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(BactaDefOf.RSW_CarryCorpseToBactaTank, corpse, tank);
            job.count = 1;
            return job;
        }

        /// <summary>Nearest reachable tank that would actually take this corpse right now.</summary>
        private static Building_BactaTank FindTank(Pawn pawn, Corpse corpse)
        {
            Thing found = GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForDef(BactaDefOf.RSW_BactaTank),
                PathEndMode.InteractionCell,
                TraverseParms.For(pawn),
                9999f,
                delegate (Thing candidate)
                {
                    Building_BactaTank tank = candidate as Building_BactaTank;
                    if (tank == null || !(bool)tank.CanAcceptCorpse(corpse))
                    {
                        return false;
                    }
                    return pawn.CanReserveAndReach(tank, PathEndMode.InteractionCell, Danger.Deadly, 1, -1, null);
                });
            return found as Building_BactaTank;
        }
    }
}
