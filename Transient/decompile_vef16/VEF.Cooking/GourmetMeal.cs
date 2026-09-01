using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Cooking;

public class GourmetMeal : ThingWithComps
{
	public override bool CanStackWith(Thing other)
	{
		if (other.def == ((Thing)this).def && ThingCompUtility.TryGetComp<CompIngredients>(other) != null && ThingCompUtility.TryGetComp<CompIngredients>((Thing)(object)this) != null && other is GourmetMeal)
		{
			List<ThingDef> ingredients = ThingCompUtility.TryGetComp<CompIngredients>(other).ingredients;
			List<ThingDef> ingredients2 = ThingCompUtility.TryGetComp<CompIngredients>((Thing)(object)this).ingredients;
			string text = "";
			string text2 = "";
			foreach (ThingDef item in ingredients)
			{
				if (item.ingredient == null)
				{
					continue;
				}
				foreach (string mergeCompatibilityTag in item.ingredient.mergeCompatibilityTags)
				{
					if (mergeCompatibilityTag == "Condiments")
					{
						text = ((Def)item).defName;
					}
				}
			}
			foreach (ThingDef item2 in ingredients2)
			{
				if (item2.ingredient == null)
				{
					continue;
				}
				foreach (string mergeCompatibilityTag2 in item2.ingredient.mergeCompatibilityTags)
				{
					if (mergeCompatibilityTag2 == "Condiments")
					{
						text2 = ((Def)item2).defName;
					}
				}
			}
			if (text == text2 || text == "" || text2 == "")
			{
				return true;
			}
			return false;
		}
		return ((ThingWithComps)this).CanStackWith(other);
	}
}
