using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // PORTED_BEAST_MECHANICS_REBUILD_1 — see CompMetalEater.cs for the header.
    //
    // Inserted at the vanilla Animal_PreMain think-tree tag, so it is consulted
    // before the ordinary satisfy-basic-needs subtree. Every animal's think runs
    // through here, so the first thing it does is the cheap comp check.
    public class JobGiver_EatMetal : ThinkNode_JobGiver
    {
        private Effecter digEffecter;

        public override float GetPriority(Pawn pawn)
        {
            if (!RSW_BeastMechanicsSettings.metalEatingEnabled)
            {
                return 0f;
            }
            Need_Food food = pawn?.needs?.food;
            if (food == null)
            {
                return 0f;
            }
            if (pawn.TryGetComp<CompMetalEater>() == null)
            {
                return 0f;
            }
            if (food.CurLevelPercentage < pawn.RaceProps.FoodLevelPercentageWantEat)
            {
                // Same number the donor used, and the same one vanilla's own
                // JobGiver_GetFood returns for a hungry animal.
                return 9.5f;
            }
            return 0f;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RSW_BeastMechanicsSettings.metalEatingEnabled)
            {
                return null;
            }
            CompMetalEater comp = pawn?.TryGetComp<CompMetalEater>();
            if (comp == null || pawn.Map == null)
            {
                return null;
            }
            Need_Food food = pawn.needs?.food;
            if (food == null || food.CurLevelPercentage >= pawn.RaceProps.FoodLevelPercentageWantEat)
            {
                return null;
            }

            Thing thing = null;
            if (comp.Props.customThingToEat != null)
            {
                foreach (string defName in comp.Props.customThingToEat)
                {
                    // GetNamedSilentFail: the list may legitimately name a def
                    // from a mod that is not loaded. That is not an error.
                    ThingDef thingDef = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                    if (thingDef == null)
                    {
                        continue;
                    }
                    thing = FindMetalInMap(thingDef, pawn);
                    if (thing != null)
                    {
                        break;
                    }
                }
            }

            if (thing != null && pawn.Map.reservationManager.CanReserve(pawn, thing, 1))
            {
                Job job = JobMaker.MakeJob(RSW_BeastMechanicsDefOf.RSW_EatMetal, thing);
                job.count = 1;
                return job;
            }

            // Nothing edible reachable. Dig some up rather than starve — this is
            // what keeps the creature alive on a map that has no loose steel.
            if (comp.Props.digThingIfMapEmpty
                && !comp.Props.thingToDigIfMapEmpty.NullOrEmpty()
                && food.CurLevelPercentage < food.PercentageThreshHungry
                && pawn.Awake())
            {
                ThingDef dugDef = DefDatabase<ThingDef>.GetNamedSilentFail(comp.Props.thingToDigIfMapEmpty);
                if (dugDef != null)
                {
                    Thing dug = null;
                    for (int i = 0; i < comp.Props.customAmountToDig; i++)
                    {
                        dug = GenSpawn.Spawn(dugDef, pawn.Position, pawn.Map, WipeMode.Vanish);
                    }
                    if (dug != null)
                    {
                        if (digEffecter == null)
                        {
                            digEffecter = EffecterDefOf.Mine.Spawn();
                        }
                        digEffecter.Trigger(pawn, dug);
                    }
                }
            }
            return null;
        }

        private static Thing FindMetalInMap(ThingDef thingDef, Pawn pawn)
        {
            bool ignoreForbidden = ForbidUtility.CaresAboutForbidden(pawn, true)
                && pawn.playerSettings != null
                && pawn.playerSettings.EffectiveAreaRestrictionInPawnCurrentMap != null;
            Thing found = GenClosest.ClosestThingReachable(
                pawn.Position, pawn.Map, ThingRequest.ForDef(thingDef), PathEndMode.ClosestTouch,
                TraverseParms.For(pawn, Danger.Deadly, TraverseMode.ByPawn, false), 9999f,
                null, null, 0, -1, false, RegionType.Set_Passable, ignoreForbidden);
            if (found != null && found.Position.InAllowedArea(pawn))
            {
                return found;
            }
            return null;
        }
    }
}
