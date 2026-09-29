using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.3: one WorkGiver "cannot switch work types" per target, so
    // this ships two (WorkGiver_ApplyDeepfireConstruction/Crafting below),
    // sharing everything but which Things they pick up. Shape (ShouldSkip +
    // PotentialWorkThingsGlobal scanning the designation, HasJobOnThing/
    // JobOnThing) copied from vanilla WorkGiver_PaintBuilding
    // (RimWorld/WorkGiver_PaintBuilding.cs, read via RimSage this pass).
    public abstract class WorkGiver_ApplyDeepfireBase : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForUndefined();

        protected abstract bool AcceptsTarget(Thing t);

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(DeepfireDefOf.RM_ApplyDeepfireDesignation);
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(DeepfireDefOf.RM_ApplyDeepfireDesignation))
            {
                Thing t = d.target.Thing;
                if (t != null && AcceptsTarget(t)) yield return t;
            }
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!AcceptsTarget(t)) return false;

            CompDeepfire comp = t.TryGetComp<CompDeepfire>();
            if (comp == null || !comp.CanAddCoat) return false;
            if (pawn.Map.designationManager.DesignationOn(t, DeepfireDefOf.RM_ApplyDeepfireDesignation) == null) return false;
            if (t.IsForbidden(pawn)) return false;
            if (!pawn.CanReserveAndReach(t, PathEndMode, Danger.Some, 1, -1, null, forced)) return false;

            int cost = DeepfireCostUtility.CostFor(t);
            Thing stack = DeepfireCostUtility.FindNearbyDeepfire(pawn, cost, forced);
            if (stack == null)
            {
                JobFailReason.Is("No deepfire available.");
                return false;
            }
            return true;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            int cost = DeepfireCostUtility.CostFor(t);
            Thing stack = DeepfireCostUtility.FindNearbyDeepfire(pawn, cost, forced);
            if (stack == null) return null;

            Job job = JobMaker.MakeJob(DeepfireDefOf.RM_ApplyDeepfire, t, stack);
            job.count = cost;
            return job;
        }
    }

    public class WorkGiver_ApplyDeepfireConstruction : WorkGiver_ApplyDeepfireBase
    {
        protected override bool AcceptsTarget(Thing t) => t.def.category == ThingCategory.Building;
    }

    public class WorkGiver_ApplyDeepfireCrafting : WorkGiver_ApplyDeepfireBase
    {
        protected override bool AcceptsTarget(Thing t) => t.def.category != ThingCategory.Building;
    }
}
