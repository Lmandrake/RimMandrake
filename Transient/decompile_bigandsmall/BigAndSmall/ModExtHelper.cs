using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class ModExtHelper
{
	public class ModExtWrapper<T>(T extension, Type sourceType, int priority) where T : DefModExtension
	{
		public T extension = extension;

		public Type sourceType = sourceType;

		public int priority = priority;
	}

	public static List<PawnExtension> GetAllPawnExtensions(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true, bool includeInactive = false, bool checkForExclusionTags = true)
	{
		List<PawnExtension> list = new List<PawnExtension>();
		if (includeInactive)
		{
			List<PawnExtension> list2 = new List<PawnExtension>();
			list2.AddRange(pawn.GetHediffExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list2.AddRange(pawn.GetApparelEtcExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list2.AddRange(pawn.GetAllGeneExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list2.AddRange(pawn.GetAllTraitExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list2.AddRange(((Def)(object)pawn.kindDef).GetAllPawnExtensions(parentWhitelist, parentBlacklist, doSort));
			list2.AddRange(((Def)(object)((Thing)pawn).def).GetAllPawnExtensions(parentWhitelist, parentBlacklist, doSort));
			list = list2;
			Pawn_RoyaltyTracker royalty = pawn.royalty;
			List<RoyalTitle> list3 = ((royalty != null) ? royalty.AllTitlesInEffectForReading : null);
			if (list3 != null)
			{
				foreach (RoyalTitle item in list3)
				{
					List<PawnExtension> allPawnExtensions = ((Def)(object)item.def).GetAllPawnExtensions(parentWhitelist, parentBlacklist, doSort);
					if (GenCollection.Any<PawnExtension>(allPawnExtensions))
					{
						list.AddRange(allPawnExtensions);
					}
				}
			}
		}
		else
		{
			List<PawnExtension> list4 = new List<PawnExtension>();
			list4.AddRange(pawn.GetHediffExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list4.AddRange(pawn.GetApparelEtcExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list4.AddRange(pawn.GetActiveGeneExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list4.AddRange(pawn.GetAllActiveTraitExtensions<PawnExtension>(parentWhitelist, parentBlacklist, doSort));
			list4.AddRange(((Def)(object)pawn.kindDef).GetAllPawnExtensions(parentWhitelist, parentBlacklist, doSort));
			list4.AddRange(((Def)(object)((Thing)pawn).def).GetAllPawnExtensions(parentWhitelist, parentBlacklist, doSort));
			list = list4;
			Pawn_RoyaltyTracker royalty2 = pawn.royalty;
			List<RoyalTitle> list5 = ((royalty2 != null) ? royalty2.AllTitlesInEffectForReading : null);
			if (list5 != null)
			{
				foreach (RoyalTitle item2 in list5)
				{
					List<PawnExtension> allPawnExtensions2 = ((Def)(object)item2.def).GetAllPawnExtensions(parentWhitelist, parentBlacklist, doSort);
					if (GenCollection.Any<PawnExtension>(allPawnExtensions2))
					{
						list.AddRange(allPawnExtensions2);
					}
				}
			}
		}
		if (checkForExclusionTags)
		{
			list = list.FilterByExclusionTags();
		}
		return list;
	}

	public static List<PawnExtension> FilterByExclusionTags(this List<PawnExtension> extensions)
	{
		List<PawnExtension> list = extensions.OrderBy((PawnExtension x) => x.priority).ToList();
		for (int num = list.Count - 1; num >= 0; num--)
		{
			PawnExtension ext = list[num];
			if (!GenList.NullOrEmpty<string>((IList<string>)ext.exclusionTags))
			{
				bool flag = false;
				foreach (string tag in ext.exclusionTags)
				{
					list = list.Where((PawnExtension x) => x == ext || x.exclusionTags == null || !x.exclusionTags.Contains(tag)).ToList();
					flag = true;
				}
				if (flag)
				{
					num = Math.Min(num, list.Count - 1);
					if (num < 0)
					{
						break;
					}
				}
			}
		}
		return list;
	}

	public static List<PawnExtension> GetAllPawnExtensionsOnHediff(this HediffDef hediffDef, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true)
	{
		return hediffDef.ExtensionsOnDef<PawnExtension, HediffDef>(parentWhitelist, parentBlacklist, doSort);
	}

	public static List<PawnExtension> GetAllPawnExtensionsOnGene(this GeneDef geneDef, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true)
	{
		return geneDef.ExtensionsOnDef<PawnExtension, GeneDef>(parentWhitelist, parentBlacklist, doSort);
	}

	public static List<PawnExtension> GetAllPawnExtensions(this Def def, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true)
	{
		return def.ExtensionsOnDef<PawnExtension, Def>(parentWhitelist, parentBlacklist, doSort);
	}

	public static List<T> GetAllExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		List<T> hediffExtensions = pawn.GetHediffExtensions<T>(parentWhitelist, parentBlacklist, doSort);
		List<T> activeGeneExtensions = pawn.GetActiveGeneExtensions<T>(parentWhitelist, parentBlacklist, doSort);
		List<T> allActiveTraitExtensions = pawn.GetAllActiveTraitExtensions<T>(parentWhitelist, parentBlacklist, doSort);
		List<T> list = new List<T>(hediffExtensions.Count + activeGeneExtensions.Count + allActiveTraitExtensions.Count);
		list.AddRange(hediffExtensions);
		list.AddRange(activeGeneExtensions);
		list.AddRange(allActiveTraitExtensions);
		return list;
	}

	public static List<T> GetAllExtensionsPlusInactive<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		List<T> hediffExtensions = pawn.GetHediffExtensions<T>(parentWhitelist, parentBlacklist, doSort);
		List<T> allGeneExtensions = pawn.GetAllGeneExtensions<T>(parentWhitelist, parentBlacklist, doSort);
		List<T> allTraitExtensions = pawn.GetAllTraitExtensions<T>(parentWhitelist, parentBlacklist, doSort);
		List<T> list = new List<T>(hediffExtensions.Count + allGeneExtensions.Count + allTraitExtensions.Count);
		list.AddRange(hediffExtensions);
		list.AddRange(allGeneExtensions);
		list.AddRange(allTraitExtensions);
		return list;
	}

	public static List<T> GetAllExtensionsOnBackStories<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		List<BackstoryDef> list = new List<BackstoryDef>(2);
		Pawn_StoryTracker story = pawn.story;
		list.Add((story != null) ? story.Childhood : null);
		Pawn_StoryTracker story2 = pawn.story;
		list.Add((story2 != null) ? story2.Adulthood : null);
		List<T> list2 = new List<T>();
		foreach (BackstoryDef item in list)
		{
			if (item != null)
			{
				list2.AddRange(item.ExtensionsOnDef<T, BackstoryDef>(parentWhitelist, parentBlacklist, doSort));
			}
		}
		return list2;
	}

	public static List<T> GetHediffExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		return GetFilteredResult(GetAllMatchingExtensionsFromHediffSetWithSource<T>(pawn), parentWhitelist, parentBlacklist, doSort);
	}

	public static List<T> GetApparelEtcExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		return GetFilteredResult(GetAllMatchingExtensionsFromApparelEtc<T>(pawn), parentWhitelist, parentBlacklist, doSort);
	}

	public static List<T> GetActiveGeneExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		return GetFilteredResult(GetAllMatchingExtensionsFromGenes<T>(pawn, active: true), parentWhitelist, parentBlacklist, doSort);
	}

	/// <summary>
	/// Also includes inactive genes.
	/// </summary>
	public static List<T> GetAllGeneExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		return GetFilteredResult(GetAllMatchingExtensionsFromGenes<T>(pawn, active: true), parentWhitelist, parentBlacklist, doSort);
	}

	public static List<T> GetAllActiveTraitExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		List<T> result = new List<T>();
		Pawn_StoryTracker story = pawn.story;
		if (story != null)
		{
			TraitSet traits = story.traits;
			bool? obj;
			if (traits == null)
			{
				obj = null;
			}
			else
			{
				List<Trait> allTraits = traits.allTraits;
				obj = ((allTraits != null) ? new bool?(GenCollection.Any<Trait>(allTraits)) : ((bool?)null));
			}
			bool? flag = obj;
			if (flag == true)
			{
				return (from x in pawn.story.traits.allTraits
					where !x.Suppressed
					select x.def).ToList().ExtensionsOnDefList<T, TraitDef>(parentWhitelist, parentBlacklist, doSort);
			}
		}
		return result;
	}

	public static List<T> GetAllTraitExtensions<T>(this Pawn pawn, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		List<T> result = new List<T>();
		Pawn_StoryTracker story = pawn.story;
		if (story != null)
		{
			TraitSet traits = story.traits;
			bool? obj;
			if (traits == null)
			{
				obj = null;
			}
			else
			{
				List<Trait> allTraits = traits.allTraits;
				obj = ((allTraits != null) ? new bool?(GenCollection.Any<Trait>(allTraits)) : ((bool?)null));
			}
			bool? flag = obj;
			if (flag == true)
			{
				return pawn.story.traits.allTraits.Select((Trait x) => x.def).ToList().ExtensionsOnDefList<T, TraitDef>(parentWhitelist, parentBlacklist, doSort);
			}
		}
		return result;
	}

	public static List<T> ExtensionsOnDef<T, TDef>(this TDef def, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension where TDef : Def
	{
		return GetFilteredResult(GetAllMatchingExtensions<T>((Def)(object)def, ((object)def).GetType()), parentWhitelist, parentBlacklist, doSort);
	}

	public static List<T> ExtensionsOnDefList<T, TDef>(this List<TDef> def, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension where TDef : Def
	{
		List<T> list = new List<T>();
		foreach (TDef item in def)
		{
			list.AddRange(item.ExtensionsOnDef<T, TDef>(parentWhitelist, parentBlacklist, doSort));
		}
		return list;
	}

	private static List<T> GetFilteredResult<T>(List<ModExtWrapper<T>> matches, List<Type> parentWhitelist = null, List<Type> parentBlacklist = null, bool doSort = true) where T : DefModExtension
	{
		List<T> list = new List<T>();
		if (doSort)
		{
			matches.OrderByDescending((ModExtWrapper<T> a) => a.priority);
		}
		if (parentWhitelist == null && parentBlacklist == null)
		{
			return matches.Select((ModExtWrapper<T> a) => a.extension).ToList();
		}
		foreach (ModExtWrapper<T> match in matches)
		{
			if ((parentWhitelist == null || parentWhitelist.Contains(match.sourceType)) && (parentBlacklist == null || !parentBlacklist.Contains(match.sourceType)))
			{
				list.Add(match.extension);
			}
		}
		return list;
	}

	private static List<ModExtWrapper<T>> GetAllMatchingExtensionsFromApparelEtc<T>(Pawn pawn) where T : DefModExtension
	{
		List<ModExtWrapper<T>> list = new List<ModExtWrapper<T>>();
		Pawn_EquipmentTracker equipment = pawn.equipment;
		if (equipment != null)
		{
			ThingWithComps primary = equipment.Primary;
			if (primary != null)
			{
				list.AddRange(GetAllMatchingExtensions<T>((Def)(object)((Thing)primary).def, ((object)primary).GetType()));
			}
		}
		Pawn_ApparelTracker apparel = pawn.apparel;
		if (((apparel != null) ? apparel.WornApparel : null) == null)
		{
			return list;
		}
		foreach (Apparel item in pawn.apparel.WornApparel)
		{
			list.AddRange(GetAllMatchingExtensions<T>((Def)(object)((Thing)item).def, ((object)item).GetType()));
		}
		return list;
	}

	private static List<ModExtWrapper<T>> GetAllMatchingExtensionsFromHediffSetWithSource<T>(Pawn pawn) where T : DefModExtension
	{
		List<ModExtWrapper<T>> list = new List<ModExtWrapper<T>>();
		if (pawn.health?.hediffSet == null)
		{
			return list;
		}
		foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
		{
			list.AddRange(GetAllMatchingExtensions<T>((Def)(object)hediff.def, ((object)hediff).GetType()));
		}
		return list;
	}

	private static List<ModExtWrapper<T>> GetAllMatchingExtensionsFromGenes<T>(Pawn pawn, bool active) where T : DefModExtension
	{
		List<ModExtWrapper<T>> list = new List<ModExtWrapper<T>>();
		if (pawn.genes == null)
		{
			return list;
		}
		foreach (Gene item in active ? pawn.GetAllActiveGenes() : GeneHelpers.GetAllGenes(pawn).ToHashSet())
		{
			list.AddRange(GetAllMatchingExtensions<T>((Def)(object)item.def, ((object)item).GetType()));
		}
		return list;
	}

	private static List<ModExtWrapper<T>> GetAllMatchingExtensions<T>(Def def, Type source) where T : DefModExtension
	{
		List<ModExtWrapper<T>> list = new List<ModExtWrapper<T>>();
		if (def?.modExtensions == null)
		{
			return list;
		}
		int num = 0;
		if (source == typeof(RaceTracker))
		{
			num = -1000;
		}
		else if (def is PawnKindDef)
		{
			num = -100;
		}
		else if (def is TraitDef)
		{
			num = -10;
		}
		else if (def is GeneDef)
		{
			num = 10;
		}
		else if (def is HediffDef)
		{
			num = 100;
		}
		foreach (DefModExtension modExtension in def.modExtensions)
		{
			T val = (T)(object)((modExtension is T) ? modExtension : null);
			if (val != null)
			{
				list.Add(new ModExtWrapper<T>(val, source, (modExtension is PawnExtension { priority: not int.MinValue } pawnExtension) ? pawnExtension.priority : num));
			}
		}
		return list;
	}
}
