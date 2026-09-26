using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TWO_FRONT_LURE_1, step 2 of 2: a Downed pawn
    /// flagged RM_Designation_StakeLure gets carried to the nearest
    /// unoccupied RM_LureStake. Shape cribbed from vanilla WorkGiver_Rescue/
    /// WorkGiver_Capture's own "victim first, destination resolved in
    /// JobOnThing" split (both read via RimSage this pass through
    /// JobDriver_TakeToBed, the Capture JobDef's real driver class).</summary>
    public class RM_WorkGiver_HaulToStake : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override System.Collections.Generic.IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RM_TwoFrontLureDefOf.RM_Designation_StakeLure))
            {
                yield return d.target.Thing;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RM_TwoFrontLureDefOf.RM_Designation_StakeLure);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!(t is Pawn victim) || victim.Dead || !victim.Downed)
            {
                return false;
            }
            if (pawn.Map.designationManager.DesignationOn(victim, RM_TwoFrontLureDefOf.RM_Designation_StakeLure) == null)
            {
                return false;
            }
            if (!pawn.CanReserve(victim, 1, -1, null, forced))
            {
                return false;
            }
            return FindStake(pawn, victim) != null;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Thing stake = FindStake(pawn, (Pawn)t);
            if (stake == null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RM_TwoFrontLureDefOf.RM_HaulToStake, t, stake);
            return job;
        }

        private Thing FindStake(Pawn pawn, Pawn victim)
        {
            return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForDef(RM_TwoFrontLureDefOf.RM_LureStake),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn),
                validator: delegate (Thing t)
                {
                    RM_CompLureStake comp = t.TryGetComp<RM_CompLureStake>();
                    if (comp == null || comp.HasLiveBait)
                    {
                        return false;
                    }
                    return pawn.CanReserve(t, 1, -1, null);
                });
        }
    }
}
