using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 7 of 8 (mechanism reference:
    /// infrastructure/state/items/RUT_SCAVENGEREVENTS_BUILD_1.md). Food-relief
    /// -when-hungry, not a calendar holiday: only fires if a random
    /// non-hostile faction exists and isn't hostile to the player, AND the
    /// colony's total human-edible nutrition is below 4x the free-colonist
    /// count. Drops 2x MealSimple + 2x MealFine (each stacked 20-40). Ported
    /// behavior-not-bugs from MoreIncidents.MOIncidentWorker_Thanksgiving --
    /// added a null-check on the non-hostile faction lookup that the donor's
    /// own decompiled IL does not have (RandomNonHostileFaction can return
    /// null, and calling .HostileTo() on that would NRE; not reproducing
    /// that crash risk).
    /// </summary>
    public class IncidentWorker_Thanksgiving : IncidentWorker
    {
        private const int DropRadius = 110;
        private const float NutritionThresholdPerColonist = 4f;
        private const int MinStack = 20;
        private const int MaxStack = 40;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!ScavengerEventsSettings.thanksgivingEnabled)
                return false;

            var map = (Map)parms.target;
            Faction nonHostile = Find.FactionManager.RandomNonHostileFaction(true, true, true, TechLevel.Neolithic);
            if (nonHostile == null || nonHostile.HostileTo(Faction.OfPlayer))
                return false;

            int colonistCount = map.mapPawns.FreeColonistsSpawnedCount;
            float threshold = NutritionThresholdPerColonist * ScavengerEventsSettings.thanksgivingThresholdMultiplier * colonistCount;
            return map.resourceCounter.TotalHumanEdibleNutrition < threshold;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;

            var contents = new List<Thing>();
            AddStackedMeal(contents, "MealSimple");
            AddStackedMeal(contents, "MealFine");
            AddStackedMeal(contents, "MealSimple");
            AddStackedMeal(contents, "MealFine");

            IntVec3 dropSpot = DropCellFinder.RandomDropSpot(map);
            DropPodUtility.DropThingsNear(dropSpot, map, contents, DropRadius, false, false, true, true, true, null);

            Find.LetterStack.ReceiveLetter(
                "RUT_Thanksgiving".Translate(),
                "RUT_ThanksgivingDesc".Translate(),
                LetterDefOf.PositiveEvent,
                new TargetInfo(dropSpot, map));

            return true;
        }

        private static void AddStackedMeal(List<Thing> contents, string defName)
        {
            Thing meal = ThingMaker.MakeThing(ThingDef.Named(defName));
            meal.stackCount = System.Math.Min(Rand.RangeInclusive(MinStack, MaxStack), meal.def.stackLimit);
            contents.Add(meal);
        }
    }
}
