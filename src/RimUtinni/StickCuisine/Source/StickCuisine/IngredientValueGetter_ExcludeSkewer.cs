using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StickCuisine
{
    // RUT_Skewer carries no <ingestible> and no Nutrition statBase, so the
    // base IngredientValueGetter_Nutrition already returns 0 for it -
    // IsNutritionGivingIngestible is false before ValuePerUnitOf is ever
    // reached. The point of this override is NOT to make the skewer worth
    // zero (it already is); it's to make it worth something COUNTABLE.
    // Verified against WorkGiver_DoBill.TryFindBestBillIngredientsInSet_AllowMix:
    // it divides the remaining required amount by ValuePerUnitOf(thing.def)
    // to size each pick, and a getter that returns 0 for the skewer makes
    // that division infinite - the loop can never subtract the skewer's
    // required count down to zero, so no bill with RUT_Skewer as an
    // ingredient can ever be satisfied. Counting it by volume (1 unit per
    // skewer) instead of by nutrition is what actually excludes it from the
    // nutrition math while keeping it requestable.
    public class IngredientValueGetter_ExcludeSkewer : IngredientValueGetter_Nutrition
    {
        public override float ValuePerUnitOf(ThingDef t)
        {
            if (t == StickCuisineDefOf.RUT_Skewer)
            {
                return 1f;
            }
            return base.ValuePerUnitOf(t);
        }
    }
}
