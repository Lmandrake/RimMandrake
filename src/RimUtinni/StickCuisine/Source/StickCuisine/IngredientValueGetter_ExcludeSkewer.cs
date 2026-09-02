using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StickCuisine
{
    // The donor mod's expansion pack (badoaks.meatonastick.expansion, workshop 3577333297)
    // uses a custom MOAS_Expansion.IngredientValueGetter_MeatlessStick on every recipe that
    // also consumes RUT_Skewer, but shipped no Source/ for it - only a compiled DLL, not
    // decompiled here. This is FOUNDRY's own reconstruction of the evident intent (every
    // recipe adds a zero-nutrition stick ingredient on top of the food ingredient; the
    // default nutrition-based value getter would otherwise average the stick's 0 nutrition
    // into the product-count/quality math), not a byte-for-byte port. Flagged as inferred,
    // not verified against the original binary.
    public class IngredientValueGetter_ExcludeSkewer : IngredientValueGetter_Nutrition
    {
        public override float ValuePerUnitOf(ThingDef t)
        {
            if (t == StickCuisineDefOf.RUT_Skewer)
            {
                return 0f;
            }
            return base.ValuePerUnitOf(t);
        }
    }
}
