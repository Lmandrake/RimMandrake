using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

/// <summary>
/// This is a list of food categories that a pawn may or may not be able to eat.
/// The default assumption is that they can not.
/// </summary>
public class NewFoodCategory : Def
{
	public class FilterListFor
	{
		public FilterListSet<FleshTypeDef> fleshTypes = new FilterListSet<FleshTypeDef>();

		public FilterListSet<ThingDef> pawnThingsDefs = new FilterListSet<ThingDef>();

		public FilterListSet<GeneDef> geneDefs = new FilterListSet<GeneDef>();
	}

	public static Dictionary<ThingDef, NewFoodCategory> foodCatagoryForFood = new Dictionary<ThingDef, NewFoodCategory>();

	public bool allowByDefault;

	public List<ThingDef> foodDefs = new List<ThingDef>();

	public FilterListFor filterListFor = new FilterListFor();

	public static NewFoodCategory FoodCatagoryForThingDef(ThingDef foodDef)
	{
		if (!foodCatagoryForFood.TryGetValue(foodDef, out var value))
		{
			return null;
		}
		return value;
	}

	public static void SetupFoodCategories()
	{
		foreach (NewFoodCategory item in DefDatabase<NewFoodCategory>.AllDefsListForReading)
		{
			foreach (ThingDef foodDef in item.foodDefs)
			{
				foodCatagoryForFood[foodDef] = item;
			}
		}
	}

	public FilterResult DefaultAcceptPawn(Pawn pawn, ICollection<GeneDef> activeGenes, List<PawnDiet> diets)
	{
		FilterResult filterResult = FilterResult.None;
		if (!GenList.NullOrEmpty<PawnDiet>((IList<PawnDiet>)diets))
		{
			filterResult = filterResult.Fuse(diets.Where((PawnDiet x) => x.newFoodCategoryFilters != null).SelectMany((PawnDiet x) => x.newFoodCategoryFilters.Items).GetFilterResult(this));
		}
		RaceProperties raceProps = pawn.RaceProps;
		FleshTypeDef item = ((raceProps != null) ? raceProps.FleshType : null);
		FilterResult? filterResult2 = filterListFor.fleshTypes?.Items.GetFilterResult(item);
		if (filterResult2.HasValue)
		{
			FilterResult valueOrDefault = filterResult2.GetValueOrDefault();
			if (valueOrDefault != 0)
			{
				filterResult = filterResult.Fuse(valueOrDefault);
			}
		}
		filterResult2 = filterListFor?.pawnThingsDefs?.Items.GetFilterResult(((Thing)pawn).def);
		if (filterResult2.HasValue)
		{
			FilterResult valueOrDefault2 = filterResult2.GetValueOrDefault();
			if (valueOrDefault2 != 0)
			{
				filterResult = filterResult.Fuse(valueOrDefault2);
			}
		}
		filterResult2 = filterListFor?.geneDefs?.Items.GetFilterResultFromItemList(new _003C_003Ez__ReadOnlyArray<GeneDef>(activeGenes.ToArray()));
		if (filterResult2.HasValue)
		{
			FilterResult valueOrDefault3 = filterResult2.GetValueOrDefault();
			if (valueOrDefault3 != 0)
			{
				filterResult = filterResult.Fuse(valueOrDefault3);
			}
		}
		if (filterResult != 0)
		{
			return filterResult;
		}
		if (!allowByDefault)
		{
			return FilterResult.Neutral;
		}
		return FilterResult.Allow;
	}
}
