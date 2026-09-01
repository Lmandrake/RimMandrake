using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

[StaticConstructorOnStartup]
public static class RecipeInheritance
{
	static RecipeInheritance()
	{
		List<ThingDef> allDefsListForReading = DefDatabase<ThingDef>.AllDefsListForReading;
		for (int i = 0; i < allDefsListForReading.Count; i++)
		{
			ThingDef val = allDefsListForReading[i];
			if (!val.IsWorkTable)
			{
				continue;
			}
			RecipeInheritanceExtension modExtension = ((Def)val).GetModExtension<RecipeInheritanceExtension>();
			if (modExtension == null || modExtension.inheritRecipesFrom == null)
			{
				continue;
			}
			List<RecipeDef> list = new List<RecipeDef>(val.AllRecipes);
			ReflectionCache.ThingDef_allRecipesCached.Invoke(val) = null;
			for (int j = 0; j < modExtension.inheritRecipesFrom.Count; j++)
			{
				ThingDef val2 = modExtension.inheritRecipesFrom[j];
				List<RecipeDef> list2 = val2.AllRecipes ?? new List<RecipeDef>();
				for (int k = 0; k < list2.Count; k++)
				{
					RecipeDef val3 = val2.AllRecipes[k];
					if (modExtension.Allows(val3))
					{
						if (val.recipes == null)
						{
							val.recipes = new List<RecipeDef>();
						}
						if (!list.Contains(val3))
						{
							val.recipes.Add(val3);
						}
					}
				}
			}
		}
	}
}
