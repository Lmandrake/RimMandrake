using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_LACQUER_BILL_AND_RIGHT_CLICK (owner ruling 2026-10-16, by card "Bill + right-click the press"; his words:
    // "That sounds like a job/recipe combo, not a special button that players need to just know will appear"). Two ways to
    // lacquer, both at the powered deepfire press, neither a pawn button:
    //   1. BILLS "Lacquer apparel" / "Lacquer weapon" (RM_LacquerApparel / RM_LacquerWeapon): one stored item plus its
    //      deepfire; the SAME item comes back with one more coat (quality, HP, style kept).
    //   2. RIGHT-CLICK the press with a colonist selected: "Lacquer <item> (N deepfire)" for each worn/held item,
    //      reusing JobDriver_LacquerWornItem.
    public class RecipeWorker_LacquerItem : RecipeWorker
    {
        public static bool IsItemSlot(Thing t) => t != null && (t.def.IsApparel || t.def.IsWeapon);

        // The item is NOT consumed: it comes back as the product (see Patch_GenRecipe_WriteCookSkill). Everything else
        // (the deepfire) is destroyed as normal.
        public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
        {
            if (IsItemSlot(ingredient)) return;
            base.ConsumeIngredient(ingredient, recipe, map);
        }

        public static bool Eligible(Thing t)
        {
            CompDeepfire comp = (t as ThingWithComps)?.GetComp<CompDeepfire>();
            return comp != null && comp.CanAddCoat && WornGlowUtility.LacquerAllowed(t);
        }

        // Add the coat and hand back the very same Thing (despawned, as a recipe product must be).
        public static IEnumerable<Thing> Products(List<Thing> ingredients)
        {
            if (ingredients == null) yield break;
            for (int i = 0; i < ingredients.Count; i++)
            {
                Thing item = ingredients[i];
                if (!IsItemSlot(item)) continue;
                if (Eligible(item)) ((ThingWithComps)item).GetComp<CompDeepfire>().AddCoat();
                if (item.Spawned) item.DeSpawn();
                yield return item;
            }
        }
    }

    // Bill ingredient search and the bill's own filter: only items that can still take a coat.
    [HarmonyPatch(typeof(Bill), nameof(Bill.IsFixedOrAllowedIngredient), new[] { typeof(Thing) })]
    public static class Patch_Bill_LacquerEligible
    {
        public static void Postfix(Bill __instance, Thing thing, ref bool __result)
        {
            if (__result && __instance.recipe?.workerClass == typeof(RecipeWorker_LacquerItem)
                && RecipeWorker_LacquerItem.IsItemSlot(thing))
                __result = RecipeWorker_LacquerItem.Eligible(thing);
        }
    }

    // Right-click the press.
    public class FloatMenuOptionProvider_LacquerAtPress : FloatMenuOptionProvider
    {
        protected override bool Drafted => false;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
        {
            if (clickedThing?.def?.defName != LacquerWornItemUtility.PressDefName) yield break;
            if (!LuminousPigmentSettings.paintingEnabled) yield break;
            Pawn pawn = context.FirstSelectedPawn;
            if (pawn == null || !pawn.IsColonistPlayerControlled) yield break;

            bool any = false;
            foreach (ThingWithComps item in WornGlowUtility.WornAndEquipped(pawn))
            {
                CompDeepfire comp = item.GetComp<CompDeepfire>();
                if (comp == null || !WornGlowUtility.LacquerAllowed(item)) continue;
                any = true;
                int cost = LacquerWornItemUtility.CostFor(item);
                string label = "Lacquer " + item.LabelShort + " (" + cost + " deepfire)";
                string why = null;
                Job job = null;
                if (!LacquerWornItemUtility.StationUsable(clickedThing)) why = "The deepfire press has no power.";
                else if (!pawn.CanReserveAndReach(clickedThing, PathEndMode.InteractionCell, Danger.Some, 1, -1, null, true)) why = "Cannot reach the press.";
                else job = LacquerWornItemUtility.MakeJob(pawn, item, clickedThing, out why);
                if (job == null)
                {
                    yield return new FloatMenuOption(label + ": " + why, null);
                    continue;
                }
                Job j = job;
                yield return new FloatMenuOption(label, delegate { pawn.jobs.TryTakeOrderedJob(j, JobTag.Misc); });
            }
            if (!any)
                yield return new FloatMenuOption("Lacquer worn item: nothing worn or held can take a coat.", null);
        }
    }
}
