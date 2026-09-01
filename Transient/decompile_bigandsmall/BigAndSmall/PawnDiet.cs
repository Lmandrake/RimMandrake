using System;
using System.Collections.Generic;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class PawnDiet : Def
{
	[Flags]
	public enum GeneralFoodCategory
	{
		Ignore = 0,
		Carnivore = 1,
		Herbivore = 2,
		ExclusiveCarnivore = 3,
		ExclusiveHerbivore = 4,
		Nothing = 5
	}

	public FilterListSet<ThingDef> foodFilters;

	public GeneralFoodCategory foodCategory;

	public FilterListSet<NewFoodCategory> newFoodCategoryFilters;

	public bool alwaysAcceptProcessed = true;

	public bool alwaysAcceptNutrientPaste = true;

	public bool alwaysAcceptNonIngestible = true;

	public Dictionary<ThingDef, FilterResult> willAcceptCacheThingless = new Dictionary<ThingDef, FilterResult>();

	public Dictionary<ThingDef, FilterResult> willAcceptCache = new Dictionary<ThingDef, FilterResult>();

	public static bool IsNutrientPaste(ThingDef foodDef)
	{
		return ((Def)foodDef).defName.Contains("NutrientPaste");
	}

	public FilterResult AcceptFoodCategory(NewFoodCategory foodCategory)
	{
		if (newFoodCategoryFilters != null)
		{
			return newFoodCategoryFilters.GetFilterResult(foodCategory);
		}
		if (!foodCategory.allowByDefault)
		{
			return FilterResult.Neutral;
		}
		return FilterResult.Allow;
	}

	public FilterResult FilterForFoodWithoutThing(ThingDef foodDef)
	{
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Invalid comparison between Unknown and I4
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Invalid comparison between Unknown and I4
		if (willAcceptCacheThingless.TryGetValue(foodDef, out var value))
		{
			return value;
		}
		FilterResult filterResult = FilterForDef(foodDef);
		if (filterResult.PriorityResult() || filterResult.Denied())
		{
			return filterResult;
		}
		if (foodCategory != 0 && foodDef.IsIngestible && !foodDef.IsProcessedFood)
		{
			filterResult = filterResult.Fuse((foodCategory switch
			{
				GeneralFoodCategory.Carnivore => (int)FoodUtility.GetFoodKind(foodDef) != 1, 
				GeneralFoodCategory.Herbivore => (int)FoodUtility.GetFoodKind(foodDef) > 0, 
				GeneralFoodCategory.Nothing => false, 
				_ => true, 
			}) ? FilterResult.Neutral : FilterResult.Deny);
		}
		willAcceptCacheThingless[foodDef] = filterResult;
		return filterResult;
	}

	public FilterResult FilterForFood(Thing food)
	{
		FilterResult filterResult = FilterForDef(food.def);
		if (filterResult.PriorityResult() || filterResult.Denied())
		{
			return filterResult;
		}
		if (foodCategory != 0 && food.def.IsIngestible && !food.def.IsProcessedFood)
		{
			return filterResult.Fuse((foodCategory switch
			{
				GeneralFoodCategory.Carnivore => FoodUtility.AcceptableCarnivore(food), 
				GeneralFoodCategory.Herbivore => FoodUtility.AcceptableVegetarian(food), 
				GeneralFoodCategory.ExclusiveCarnivore => FoodUtility.AcceptableCarnivore(food) && !FoodUtility.AcceptableVegetarian(food), 
				GeneralFoodCategory.ExclusiveHerbivore => FoodUtility.AcceptableVegetarian(food) && !FoodUtility.AcceptableCarnivore(food), 
				GeneralFoodCategory.Nothing => false, 
				_ => true, 
			}) ? FilterResult.Neutral : FilterResult.Deny);
		}
		return filterResult;
	}

	private FilterResult FilterForDef(ThingDef foodDef)
	{
		if (willAcceptCache.TryGetValue(foodDef, out var value))
		{
			return value;
		}
		FilterResult filterResult = FilterResult.Neutral;
		if (alwaysAcceptNonIngestible && !foodDef.IsIngestible)
		{
			return FilterResult.ForceAllow;
		}
		if (alwaysAcceptProcessed && foodDef.IsProcessedFood)
		{
			return FilterResult.ForceAllow;
		}
		if (alwaysAcceptNutrientPaste && IsNutrientPaste(foodDef))
		{
			return FilterResult.ForceAllow;
		}
		if (foodFilters != null)
		{
			FilterResult filterResult2 = foodFilters.GetFilterResult(foodDef);
			filterResult = filterResult.Fuse(filterResult2);
		}
		willAcceptCache[foodDef] = filterResult;
		return filterResult;
	}
}
