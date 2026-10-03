using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1: the SUPPRESSION half of the water truce.
    // A predator (any race.predator, wild or tame) never starts a hunt whose prey stands within the truce
    // radius of truce water, never targets prey while standing in it, and abandons a running hunt that
    // crosses into it. Seams (decompiled 1.6): FoodUtility.IsAcceptablePreyFor (public; the only filter the
    // private BestPawnToHuntForPredator uses) and JobDriver_PredatorHunt.MakeNewToils (fail conditions).
    // Player-ordered hunting (WorkGiver_HunterHunt) never passes through either. Reads the same field as
    // retribution (RM_MapComponent_WaterTruce.IsTruceWater), so one radius governs the whole truce.
    public static class RM_WaterTruceHuntSuppression
    {
        public static bool Blocks(Pawn predator, Pawn prey)
        {
            if (!RM_EnvironmentalHazardsSettings.waterTruceSuppressionEnabled) return false;
            Map map = predator?.Map;
            if (map == null || prey == null || prey.Map != map) return false;
            RM_MapComponent_WaterTruce truce = map.GetComponent<RM_MapComponent_WaterTruce>();
            if (truce == null || !truce.Active) return false;
            return (prey.Spawned && truce.IsTruceWater(prey.Position))
                || (predator.Spawned && truce.IsTruceWater(predator.Position));
        }

        public static void IsAcceptablePreyFor_Postfix(Pawn predator, Pawn prey, ref bool __result)
        {
            if (__result && Blocks(predator, prey)) __result = false;
        }

        public static void MakeNewToils_Postfix(JobDriver __instance, ref IEnumerable<Toil> __result)
        {
            __result = Wrap(__instance, __result);
        }

        private static IEnumerable<Toil> Wrap(JobDriver driver, IEnumerable<Toil> toils)
        {
            foreach (Toil toil in toils)
            {
                toil.AddFailCondition(() =>
                {
                    Pawn prey = driver.job?.GetTarget(TargetIndex.A).Thing as Pawn;   // a Corpse target is not a Pawn: eating is never cut short
                    return prey != null && !prey.Dead && Blocks(driver.pawn, prey);
                });
                yield return toil;
            }
        }
    }
}
