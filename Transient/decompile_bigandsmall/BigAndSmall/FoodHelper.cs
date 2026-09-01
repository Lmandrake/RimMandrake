using System.Collections.Generic;
using BigAndSmall.FilteredLists;
using Verse;

namespace BigAndSmall;

public static class FoodHelper
{
	public static FilterResult GetFilterForFoodThingDef(this ThingDef foodDef, BSCache cache)
	{
		NewFoodCategory newFoodCategory = GenCollection.TryGetValue<ThingDef, NewFoodCategory>((IReadOnlyDictionary<ThingDef, NewFoodCategory>)NewFoodCategory.foodCatagoryForFood, foodDef, (NewFoodCategory)null);
		FilterResult filterResult = FilterResult.None;
		if (newFoodCategory != null)
		{
			List<NewFoodCategory> newFoodCatDeny = cache.newFoodCatDeny;
			if (newFoodCatDeny != null && newFoodCatDeny.Contains(newFoodCategory))
			{
				filterResult = filterResult.Fuse(FilterResult.Deny);
			}
			else
			{
				List<NewFoodCategory> newFoodCatAllow = cache.newFoodCatAllow;
				filterResult = ((newFoodCatAllow == null || !newFoodCatAllow.Contains(newFoodCategory)) ? filterResult.Fuse(newFoodCategory.allowByDefault ? FilterResult.Allow : FilterResult.Deny) : filterResult.Fuse(FilterResult.Allow));
			}
		}
		return filterResult;
	}

	public static FilterResult FilterForFoodThing(this Thing food, BSCache cache)
	{
		FilterResult filterResult = FilterResult.None;
		if (!GenList.NullOrEmpty<PawnDiet>((IList<PawnDiet>)cache.pawnDiet))
		{
			int count = cache.pawnDiet.Count;
			for (int i = 0; i < count; i++)
			{
				FilterResult filterResult2 = cache.pawnDiet[i].FilterForFood(food);
				if (filterResult2.Denied())
				{
					return filterResult2;
				}
				if ((int)filterResult2 > (int)filterResult)
				{
					filterResult = filterResult2;
				}
			}
		}
		return filterResult;
	}
}
