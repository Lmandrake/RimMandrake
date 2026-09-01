using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class RecipeInheritanceExtension : DefModExtension
{
	public ThingFilter allowedProductFilter;

	public List<RecipeDef> allowedRecipes;

	public ThingFilter disallowedProductFilter;

	public List<RecipeDef> disallowedRecipes;

	public List<ThingDef> inheritRecipesFrom;

	public bool Allows(RecipeDef recipe)
	{
		ThingDef producedThingDef = recipe.ProducedThingDef;
		if ((producedThingDef == null || ((allowedProductFilter == null || allowedProductFilter.Allows(producedThingDef)) && (disallowedProductFilter == null || !disallowedProductFilter.Allows(producedThingDef)))) && (allowedRecipes == null || allowedRecipes.Contains(recipe)))
		{
			if (disallowedRecipes != null)
			{
				return !disallowedRecipes.Contains(recipe);
			}
			return true;
		}
		return false;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		if (inheritRecipesFrom == null)
		{
			yield return "inheritRecipesFrom is null.";
			yield break;
		}
		List<string> list = new List<string>();
		for (int i = 0; i < inheritRecipesFrom.Count; i++)
		{
			ThingDef val = inheritRecipesFrom[i];
			if (!val.IsWorkTable)
			{
				list.Add(((Def)val).defName);
			}
		}
		if (GenCollection.Any<string>(list))
		{
			yield return "the following ThingDefs in inheritRecipesFrom are not workbenches: " + GenText.ToCommaList((IEnumerable<string>)list, false, false);
		}
	}
}
