using RimMandrake.Pyrelands;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// DEEP_TRIBES_FIRE_RITE_1 — "then harvesting the scorch fruit" (owner,
    /// 2026-09-16). Hung on the RUT_RiteHarvest duty, so it only ever runs for a
    /// pawn the rite's Lord is holding.
    ///
    /// TWO JOBS, both vanilla drivers, in this order:
    ///   1. PICK UP what is already lying there. JobDriver_PlantWork drops the
    ///      yield at the harvester's feet and, for a non-player faction, marks it
    ///      forbidden — forbidden to the PLAYER, which is exactly right: the
    ///      colony may not just walk off with the Tribes' harvest. So a second
    ///      pass with JobDefOf.TakeInventory is what actually gets the fruit off
    ///      the map in their hands, and it also sweeps up pods the player's own
    ///      burn already opened.
    ///   2. HARVEST a pod. JobDefOf.Harvest (JobDriver_PlantHarvest) has no
    ///      RequiredDesignation, so a non-player pawn can run it on any plant with
    ///      a harvestedThingDef — no designator, no work-giver, no player
    ///      involvement.
    ///
    /// 🔴 THE DEFNAMES ARE NOT OURS AND ARE NOT GUESSED. RM_FE_Plant_ScorchFruit
    /// and RM_FE_ScorchFruitYield are read off
    /// src/RimMandrake/Pyrelands/Defs/ThingDefs_ScorchFruit/ScorchFruit.xml
    /// (harvestedThingDef RM_FE_ScorchFruitYield, harvestYield 5). They are
    /// resolved with GetNamedSilentFail, not DefOf, because mandrake.rm.pyrelands
    /// is a separate mod that a player may not have enabled — without it the rite
    /// still happens and the party simply mills about the burn and leaves.
    ///
    /// RANGE AND FULLNESS (RITE_HARVEST_FIX_PICKS_PAST_FULL, 2026-10-15): both searches range FireRiteHarvestRadius
    /// around the rite's ORIGIN (the duty focus), not around the harvester, so the range cannot walk across the map
    /// with the harvester. A harvester carrying its fireRiteCarryPerPawn neither picks up nor cuts another pod: a pod
    /// cut by a pawn that will not carry the yield only leaves fruit to spoil.
    ///
    /// ⚠️ A BURNING CELL IS NEVER A TARGET. That one validator is the whole of the
    /// "safe standoff": the pods behind the front are cold, the pods in the front
    /// are not, and a harvester will not walk into a fire to reach either. No
    /// avoidance pathing of ours.
    /// </summary>
    public class JobGiver_RUT_HarvestScorchFruit : ThinkNode_JobGiver
    {
        private const string PlantDefName = "RM_FE_Plant_ScorchFruit";
        private const string YieldDefName = "RM_FE_ScorchFruitYield";

        protected override Job TryGiveJob(Pawn pawn)
        {
            Map map = pawn?.Map;
            if (map == null || pawn.mindState?.duty == null)
            {
                return null;
            }

            // Range is centred on the rite's origin (the duty focus); a duty with no focus falls back to the harvester.
            PawnDuty duty = pawn.mindState.duty;
            IntVec3 origin = duty.focus.IsValid ? duty.focus.Cell : pawn.Position;
            float radius = duty.radius > 0f ? duty.radius : RimMandrake.Pyrelands.PyrelandsTuning.FireRiteHarvestRadius;
            // GenClosest searches from the harvester; this reach covers every cell inside the origin's radius.
            float reach = pawn.Position.DistanceTo(origin) + radius;

            ThingDef yieldDef = DefDatabase<ThingDef>.GetNamedSilentFail(YieldDefName);
            if (yieldDef != null)
            {
                int carried = pawn.inventory?.innerContainer?.TotalStackCountOfDef(yieldDef) ?? 0;
                // Reads the SETTING, not the const: the const is only its default.
                int wanted = RM_BurnKernel.RiteHarvestWanted(PyrelandsMechanicsSettings.fireRiteCarryPerPawn, carried);
                if (wanted <= 0)
                {
                    return null;   // full: no more picking up, and no cutting pods it will not carry
                }
                Thing loose = GenClosest.ClosestThingReachable(
                    pawn.Position, map,
                    ThingRequest.ForDef(yieldDef),
                    PathEndMode.ClosestTouch,
                    TraverseParms.For(pawn),
                    reach,
                    t => InRiteRange(t, origin, radius) && Reachable(pawn, t));

                if (loose != null)
                {
                    Job take = JobMaker.MakeJob(JobDefOf.TakeInventory, loose);
                    take.count = Mathf.Min(wanted, loose.stackCount);
                    return take;
                }
            }

            ThingDef plantDef = DefDatabase<ThingDef>.GetNamedSilentFail(PlantDefName);
            if (plantDef == null)
            {
                return null;
            }

            Thing pod = GenClosest.ClosestThingReachable(
                pawn.Position, map,
                ThingRequest.ForDef(plantDef),
                PathEndMode.Touch,
                TraverseParms.For(pawn),
                reach,
                t => t is Plant plant && plant.HarvestableNow && InRiteRange(t, origin, radius) && Reachable(pawn, t));

            return pod == null ? null : JobMaker.MakeJob(JobDefOf.Harvest, pod);
        }

        private static bool InRiteRange(Thing t, IntVec3 origin, float radius)
        {
            return RM_BurnKernel.RiteHarvestInRange(t.Position.x - origin.x, t.Position.z - origin.z, radius);
        }

        private static bool Reachable(Pawn pawn, Thing t)
        {
            if (t == null || !t.Spawned || t.IsBurning())
            {
                return false;
            }
            if (t.Position.GetFirstThing(t.Map, ThingDefOf.Fire) != null)
            {
                return false;
            }
            return pawn.CanReserve(t);
        }
    }
}
