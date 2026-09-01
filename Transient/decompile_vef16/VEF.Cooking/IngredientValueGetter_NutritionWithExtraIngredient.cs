using RimWorld;
using Verse;

namespace VEF.Cooking;

public class IngredientValueGetter_NutritionWithExtraIngredient : IngredientValueGetter_Nutrition
{
	public override float ValuePerUnitOf(ThingDef t)
	{
		if (!t.IsNutritionGivingIngestible)
		{
			return 1f;
		}
		if (t.ingredient != null && t.ingredient.mergeCompatibilityTags.Contains("Condiments"))
		{
			return 1f;
		}
		return StatExtension.GetStatValueAbstract((BuildableDef)(object)t, StatDefOf.Nutrition, (ThingDef)null);
	}
}
