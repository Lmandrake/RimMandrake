using System.Collections.Generic;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Lacquer bill (owner ruling 2026-10-16): drives the recipe's three real hooks (eligibility, ConsumeIngredient, product
    // list) on a spawned parka without waiting for a pawn to take a bill, and writes one "[DeepfireLacquerBill] {json}" line.
    public static class LacquerAtPressDebugActions
    {
        private const string Tag = "[DeepfireLacquerBill] ";

        [DebugAction("Deepfire", "Lacquer bill: round trip at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RoundTrip()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            Thing parka = ThingMaker.MakeThing(ThingDef.Named("Apparel_Parka"), ThingDefOf.Cloth);
            GenSpawn.Spawn(parka, c, map);
            Thing deepfire = ThingMaker.MakeThing(ThingDef.Named("RM_Deepfire"));
            deepfire.stackCount = LacquerWornItemUtility.CostFor(parka);
            GenPlace.TryPlaceThing(deepfire, c + new IntVec3(1, 0, 0), map, ThingPlaceMode.Near);

            CompDeepfire comp = ((ThingWithComps)parka).GetComp<CompDeepfire>();
            bool eligibleBefore = RecipeWorker_LacquerItem.Eligible(parka);
            int coatsBefore = comp?.coats ?? -1;
            int hpBefore = parka.HitPoints;
            QualityCategory q = QualityCategory.Normal;
            bool hadQuality = parka.TryGetQuality(out q);

            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RM_LacquerApparel");
            var ingredients = new List<Thing> { parka, deepfire };
            var worker = recipe?.Worker as RecipeWorker_LacquerItem;
            var products = new List<Thing>();
            if (worker != null)
            {
                foreach (Thing t in RecipeWorker_LacquerItem.Products(ingredients)) products.Add(t);
                foreach (Thing ing in ingredients) worker.ConsumeIngredient(ing, recipe, map);
            }
            Thing back = products.Count == 1 ? products[0] : null;
            QualityCategory q2 = QualityCategory.Normal;
            bool hasQ2 = back != null && back.TryGetQuality(out q2);
            string ids = "{\"action\":\"lacquerBillRoundTrip\",\"recipeFound\":" + (recipe != null ? "true" : "false")
                + ",\"workerOk\":" + (worker != null ? "true" : "false")
                + ",\"eligibleBefore\":" + (eligibleBefore ? "true" : "false")
                + ",\"coatsBefore\":" + coatsBefore
                + ",\"coatsAfter\":" + (comp?.coats ?? -1)
                + ",\"productCount\":" + products.Count
                + ",\"sameItem\":" + (back == parka ? "true" : "false")
                + ",\"itemAlive\":" + (!parka.Destroyed ? "true" : "false")
                + ",\"itemDespawned\":" + (!parka.Spawned ? "true" : "false")
                + ",\"hpKept\":" + (back != null && back.HitPoints == hpBefore ? "true" : "false")
                + ",\"qualityKept\":" + (!hadQuality || (hasQ2 && q2 == q) ? "true" : "false")
                + ",\"deepfireDestroyed\":" + (deepfire.Destroyed ? "true" : "false")
                + ",\"costN\":" + LacquerWornItemUtility.CostFor(parka)
                + ",\"recipeCount\":" + (recipe != null && recipe.ingredients.Count > 1 ? (int)recipe.ingredients[1].GetBaseCount() : -1)
                + "}";
            if (back != null && !back.Destroyed) back.Destroy();
            if (!deepfire.Destroyed) deepfire.Destroy();
            Log.Message(Tag + ids);
        }
    }
}
