using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class HumanPatcher
{
	private static List<ThingDef> raceThingList = new List<ThingDef>();

	private static List<(ThingDef thing, List<RaceExtension> raceExts)> thingsWithRaceExtension = new List<(ThingDef, List<RaceExtension>)>();

	public static Dictionary<BodyPartDef, List<BodyPartDef>> partImportsFromDict = new Dictionary<BodyPartDef, List<BodyPartDef>>();

	public static Dictionary<BodyPartDef, List<BodyPartDef>> partImportsFromDictReverse = new Dictionary<BodyPartDef, List<BodyPartDef>>();

	public static void PatchRecipes()
	{
		MigrateThingDefLinks();
		PatchCustomBodyPartDefs();
	}

	private static List<RecipeDef> AllHumanRecipes()
	{
		ThingDef human = ThingDefOf.Human;
		List<RecipeDef> list = new List<RecipeDef>();
		if (human.recipes != null)
		{
			for (int i = 0; i < human.recipes.Count; i++)
			{
				GenCollection.AddDistinct<RecipeDef>(list, human.recipes[i]);
			}
		}
		List<RecipeDef> allDefsListForReading = DefDatabase<RecipeDef>.AllDefsListForReading;
		for (int j = 0; j < allDefsListForReading.Count; j++)
		{
			if (allDefsListForReading[j].recipeUsers != null && allDefsListForReading[j].recipeUsers.Contains(human))
			{
				GenCollection.AddDistinct<RecipeDef>(list, allDefsListForReading[j]);
			}
		}
		return list;
	}

	private static void MigrateThingDefLinks()
	{
		raceThingList = DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x.race != null).ToList();
		thingsWithRaceExtension = (from x in DefDatabase<ThingDef>.AllDefs
			where GenCollection.Any<RaceExtension>(x.GetRaceExtensions())
			select x into td
			select (td: td, td.GetRaceExtensions())).ToList();
		List<ThingDef> humanlikes = HumanLikes.Humanlikes;
		List<ThingDef> list = (from x in thingsWithRaceExtension
			where x.raceExts.All((RaceExtension sr) => !sr.SurgeryRecipes.AnyItems())
			select x.thing).ToList();
		List<ThingDef> list2 = humanlikes;
		List<ThingDef> list3 = new List<ThingDef>(list.Count + list2.Count);
		list3.AddRange(list);
		list3.AddRange(list2);
		List<RecipeDef> list4 = AllHumanRecipes();
		foreach (ThingDef thing in list3)
		{
			foreach (RecipeDef item in list4.Where((RecipeDef x) => !thing.recipes.Contains(x)))
			{
				ThingDef val = thing;
				if (val.recipes == null)
				{
					val.recipes = new List<RecipeDef>();
				}
				GenCollection.AddDistinct<RecipeDef>(thing.recipes, item);
			}
		}
		IEnumerable<RecipeDef> allDefs = DefDatabase<RecipeDef>.AllDefs;
		foreach (RecipeDef item2 in allDefs)
		{
			if (GenCollection.Any<RecipeExtension>(item2.ExtensionsOnDef<RecipeExtension, RecipeDef>((List<Type>)null, (List<Type>)null, doSort: true), (Predicate<RecipeExtension>)((RecipeExtension x) => x.isSurgery == true)))
			{
				item2.isSurgeryCached = true;
			}
		}
		foreach (var item3 in thingsWithRaceExtension.Where(((ThingDef thing, List<RaceExtension> raceExts) x) => GenCollection.Any<RaceExtension>(x.raceExts, (Predicate<RaceExtension>)((RaceExtension r) => r.SurgeryRecipes.AnyItems()))))
		{
			var (thing2, _) = item3;
			foreach (RaceExtension item4 in item3.raceExts)
			{
				FilterListSet<RecipeDef> rFilter = item4.SurgeryRecipes;
				if (rFilter == null)
				{
					continue;
				}
				bool forceMechanical = GenCollection.Any<HediffDef>(item4.RaceHediffs, (Predicate<HediffDef>)((HediffDef x) => GenCollection.Any<PawnExtension>(x.GetAllPawnExtensionsOnHediff(), (Predicate<PawnExtension>)((PawnExtension y) => y.isMechanical))));
				IEnumerable<RecipeDef> collection = list4.Where((RecipeDef x) => rFilter.GetFilterResult(x).Accepted());
				IEnumerable<RecipeDef> enumerable = allDefs.Where((RecipeDef x) => ((Def)x).GetModExtension<RecipeExtension>()?.ShouldAddToRace(thing2, forceMechanical) ?? false);
				if (enumerable.Any())
				{
					foreach (RecipeDef item5 in enumerable)
					{
						ThingDef val = thing2;
						if (val.recipes == null)
						{
							val.recipes = new List<RecipeDef>();
						}
						GenCollection.AddDistinct<RecipeDef>(thing2.recipes, item5);
						item5.isSurgeryCached = true;
					}
				}
				IEnumerable<RecipeDef> collection2 = allDefs.Where((RecipeDef x) => rFilter.GetFilterResult(x).ExplicitlyAllowed());
				thing2.recipes.AddRange(collection);
				thing2.recipes.AddRange(enumerable);
				thing2.recipes.AddRange(collection2);
				thing2.recipes = thing2.recipes.Distinct().ToList();
			}
		}
		AddConditionalRecipes(allDefs);
		foreach (RecipeDef recipe in list4)
		{
			foreach (ThingDef item6 in humanlikes.Where((ThingDef x) => !x.recipes.Contains(recipe)))
			{
				ThingDef val;
				ThingDef obj = (val = item6);
				if (val.recipes == null)
				{
					val.recipes = new List<RecipeDef>();
				}
				GenCollection.AddDistinct<RecipeDef>(obj.recipes, recipe);
			}
		}
		foreach (ThingDef item7 in raceThingList.Distinct())
		{
			if (item7.IsMechanicalDef() && item7.race?.corpseDef != null)
			{
				ThingDef corpseDef = item7.race.corpseDef;
				BSDefs.BS_SmashRobot.fixedIngredientFilter.SetAllow(corpseDef, true);
				BSDefs.BS_ShredRobot.fixedIngredientFilter.SetAllow(corpseDef, true);
			}
		}
	}

	public static void MechanicalSetup()
	{
	}

	public static void MechanicalCorpseSetup()
	{
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		raceThingList = DefDatabase<ThingDef>.AllDefs.Where((ThingDef x) => x.race != null).ToList();
		foreach (ThingDef item in raceThingList.Distinct())
		{
			if (!item.IsMechanicalDef() || item.race?.corpseDef == null)
			{
				continue;
			}
			ThingDef corpseDef;
			ThingDef obj = (corpseDef = item.race.corpseDef);
			if (corpseDef.thingCategories == null)
			{
				corpseDef.thingCategories = new List<ThingCategoryDef>();
			}
			IngestibleProperties ingestible = obj.ingestible;
			if (ingestible != null)
			{
				ingestible.preferability = (FoodPreferability)1;
			}
			obj.comps.RemoveAll((CompProperties compProperties) => compProperties is CompProperties_SpawnerFilth);
			foreach (CompProperties_Rottable item2 in obj.comps.Where((CompProperties x) => x is CompProperties_Rottable).Cast<CompProperties_Rottable>())
			{
				item2.daysToDessicated = 999f;
				item2.daysToRotStart = 999f;
				item2.rotDamagePerDay = 10f;
			}
		}
	}

	private static void AddConditionalRecipes(IEnumerable<RecipeDef> allRecipes)
	{
		List<ThingDef> list = raceThingList.Where((ThingDef x) => thingsWithRaceExtension.All(((ThingDef thing, List<RaceExtension> raceExts) y) => y.thing != x)).ToList();
		foreach (RecipeDef item in allRecipes.Where((RecipeDef x) => !GenList.NullOrEmpty<RecipeExtension>((IList<RecipeExtension>)x.ExtensionsOnDef<RecipeExtension, RecipeDef>((List<Type>)null, (List<Type>)null, doSort: true))))
		{
			List<RecipeExtension> list2 = item.ExtensionsOnDef<RecipeExtension, RecipeDef>((List<Type>)null, (List<Type>)null, doSort: true);
			if (GenCollection.Any<RecipeExtension>(list2, (Predicate<RecipeExtension>)((RecipeExtension x) => x.isSurgery == true)))
			{
				item.isSurgeryCached = true;
			}
			foreach (ThingDef raceThing in list)
			{
				if (GenCollection.Any<RecipeExtension>(list2, (Predicate<RecipeExtension>)((RecipeExtension x) => x.ShouldAddToRace(raceThing))))
				{
					ThingDef val = raceThing;
					if (val.recipes == null)
					{
						val.recipes = new List<RecipeDef>();
					}
					GenCollection.AddDistinct<RecipeDef>(raceThing.recipes, item);
					RecipeDef val2 = item;
					if (val2.recipeUsers == null)
					{
						val2.recipeUsers = new List<ThingDef>();
					}
					GenCollection.AddDistinct<ThingDef>(item.recipeUsers, raceThing);
				}
			}
		}
	}

	private static void PatchCustomBodyPartDefs()
	{
		List<(BodyPartDef bd, List<BodyPartDef>)> list = DefDatabase<BodyPartDef>.AllDefs.Where((BodyPartDef x) => ((Def)x).modExtensions != null && GenCollection.Any<DefModExtension>(((Def)x).modExtensions, (Predicate<DefModExtension>)((DefModExtension y) => y is BodyPartExtension))).Select(delegate(BodyPartDef bd)
		{
			HashSet<BodyPartDef> hashSet = new HashSet<BodyPartDef>();
			foreach (BodyPartExtension item3 in from x in ((Def)bd).modExtensions
				where x is BodyPartExtension
				select x into bpe
				select bpe as BodyPartExtension)
			{
				GenCollection.AddRange<BodyPartDef>(hashSet, item3.importAllRecipesFrom);
			}
			return (bd: bd, hashSet.ToList());
		}).ToList();
		IEnumerable<RecipeDef> allDefs = DefDatabase<RecipeDef>.AllDefs;
		foreach (var item4 in list)
		{
			IEnumerable<BodyPartDef> item = item4.Item2;
			BodyPartDef item2 = item4.bd;
			IEnumerable<BodyPartDef> partsToCopyFrom = item;
			partImportsFromDict[item2] = partsToCopyFrom.ToList();
			foreach (RecipeDef item5 in allDefs.Where((RecipeDef x) => GenCollection.Any<BodyPartDef>(x.appliedOnFixedBodyParts, (Predicate<BodyPartDef>)((BodyPartDef y) => partsToCopyFrom.Contains(y)))))
			{
				if (!item5.appliedOnFixedBodyParts.Contains(item2))
				{
					GenCollection.AddDistinct<BodyPartDef>(item5.appliedOnFixedBodyParts, item2);
				}
			}
		}
		foreach (KeyValuePair<BodyPartDef, List<BodyPartDef>> item6 in partImportsFromDict)
		{
			foreach (BodyPartDef item7 in item6.Value)
			{
				if (!partImportsFromDictReverse.TryGetValue(item7, out var value))
				{
					value = new List<BodyPartDef>();
					partImportsFromDictReverse[item7] = value;
				}
				GenCollection.AddDistinct<BodyPartDef>(value, item6.Key);
			}
		}
		if (!partImportsFromDictReverse.ContainsKey(BSDefs.Brain))
		{
			partImportsFromDictReverse[BSDefs.Brain] = new List<BodyPartDef>();
		}
		partImportsFromDictReverse[BSDefs.Brain].Add(BSDefs.ArtificialBrain);
	}
}
