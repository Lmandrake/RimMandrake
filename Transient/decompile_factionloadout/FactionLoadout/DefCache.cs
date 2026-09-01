using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Modules;
using RimWorld;
using Verse;

namespace FactionLoadout;

public static class DefCache
{
	public static List<string> AllTechHediffTags;

	public static List<string> AllApparelTags;

	public static List<string> AllWeaponsTags;

	public static List<BodyTypeDef> AllBodyTypes;

	public static List<ThingDef> AllApparel;

	public static List<ThingDef> AllWeapons;

	public static List<ThingDef> AllTech;

	public static List<ThingDef> AllInvItems;

	public static List<ThingDef> AllHumanlikeRaces;

	public static List<PawnKindDef> AllAnimalKindDefs;

	public static List<RulePackDef> AllRulePackDefs;

	public static List<GeneDef> AllGeneDefs;

	public static Dictionary<FactionDef, List<PawnKindDef>> DefaultFactionKinds;

	public static List<string> AllBackstoryCategories;

	public static List<BackstoryDef> AllChildhoodBackstories;

	public static List<BackstoryDef> AllAdulthoodBackstories;

	public static List<BackstoryDef> AllBackstoryDefs;

	public static List<(TraitDef def, int degree)> AllTraitDegrees;

	public static List<string> AllPowerDefs;

	public static Dictionary<PawnKindDef, HashSet<ThingDef>> ApparelBlacklistCache = new Dictionary<PawnKindDef, HashSet<ThingDef>>();

	public static Dictionary<PawnKindDef, HashSet<ThingDef>> WeaponBlacklistCache = new Dictionary<PawnKindDef, HashSet<ThingDef>>();

	public static Dictionary<PawnKindDef, (HashSet<ThingDef> defs, bool blocklist)> ApparelMaterialCache = new Dictionary<PawnKindDef, (HashSet<ThingDef>, bool)>();

	public static Dictionary<PawnKindDef, (HashSet<ThingDef> defs, bool blocklist)> WeaponMaterialCache = new Dictionary<PawnKindDef, (HashSet<ThingDef>, bool)>();

	public static RulePackDef FakeRulePack = new RulePackDef
	{
		defName = "NONE"
	};

	public static void ScanDefs()
	{
		//IL_029b: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a1: Invalid comparison between Unknown and I4
		//IL_0597: Unknown result type (might be due to invalid IL or missing references)
		if (AllTechHediffTags != null)
		{
			return;
		}
		HashSet<string> hashSet = new HashSet<string>(128);
		HashSet<string> hashSet2 = new HashSet<string>(128);
		HashSet<string> hashSet3 = new HashSet<string>(128);
		HashSet<ThingDef> hashSet4 = new HashSet<ThingDef>(256);
		HashSet<ThingDef> hashSet5 = new HashSet<ThingDef>(256);
		HashSet<ThingDef> hashSet6 = new HashSet<ThingDef>(256);
		HashSet<ThingDef> hashSet7 = new HashSet<ThingDef>(128);
		HashSet<ThingDef> hashSet8 = new HashSet<ThingDef>(1024);
		HashSet<PawnKindDef> hashSet9 = new HashSet<PawnKindDef>(1024);
		HashSet<RulePackDef> hashSet10 = new HashSet<RulePackDef>(1024);
		HashSet<BodyTypeDef> hashSet11 = new HashSet<BodyTypeDef>(32);
		HashSet<GeneDef> hashSet12 = new HashSet<GeneDef>(1024);
		Dictionary<FactionDef, List<PawnKindDef>> dictionary = new Dictionary<FactionDef, List<PawnKindDef>>(64);
		foreach (PawnKindDef item in DefDatabase<PawnKindDef>.AllDefsListForReading)
		{
			RaceProperties raceProps = item.RaceProps;
			if (raceProps != null && raceProps.Animal && raceProps.packAnimal)
			{
				hashSet9.Add(item);
			}
			if (item.defaultFactionDef != null)
			{
				if (!dictionary.TryGetValue(item.defaultFactionDef, out var value))
				{
					value = new List<PawnKindDef>();
					dictionary[item.defaultFactionDef] = value;
				}
				value.Add(item);
			}
		}
		DefaultFactionKinds = dictionary;
		foreach (ThingDef item2 in DefDatabase<ThingDef>.AllDefsListForReading)
		{
			RaceProperties raceProps = item2.race;
			if (raceProps != null && !raceProps.Animal)
			{
				hashSet5.Add(item2);
			}
			if (item2.isTechHediff && !item2.IsNaturalOrgan)
			{
				if (item2.techHediffsTags != null)
				{
					foreach (string techHediffsTag in item2.techHediffsTags)
					{
						if (techHediffsTag != null)
						{
							hashSet.Add(techHediffsTag);
						}
					}
				}
				hashSet7.Add(item2);
			}
			if (item2.IsApparel)
			{
				if (item2.apparel?.tags != null)
				{
					foreach (string tag in item2.apparel.tags)
					{
						if (tag != null)
						{
							hashSet2.Add(tag);
						}
					}
				}
				hashSet4.Add(item2);
			}
			if (item2.IsWeapon)
			{
				if (item2.weaponTags != null)
				{
					foreach (string weaponTag in item2.weaponTags)
					{
						if (weaponTag != null)
						{
							hashSet3.Add(weaponTag);
						}
					}
				}
				hashSet6.Add(item2);
			}
			if ((int)item2.category == 2)
			{
				hashSet8.Add(item2);
			}
		}
		GenCollection.AddRange<BodyTypeDef>(hashSet11, DefDatabase<BodyTypeDef>.AllDefsListForReading);
		GenCollection.AddRange<RulePackDef>(hashSet10, DefDatabase<RulePackDef>.AllDefsListForReading);
		GenCollection.AddRange<GeneDef>(hashSet12, DefDatabase<GeneDef>.AllDefsListForReading);
		AllTechHediffTags = hashSet.ToList();
		AllTechHediffTags.Sort();
		hashSet2.Add("UNUSED");
		AllApparelTags = hashSet2.ToList();
		AllApparelTags.Sort();
		AllWeaponsTags = hashSet3.ToList();
		AllWeaponsTags.Sort();
		AllApparel = hashSet4.ToList();
		AllApparel.Sort((ThingDef a, ThingDef b) => TaggedString.op_Implicit(((Def)a).LabelCap).CompareTo(TaggedString.op_Implicit(((Def)b).LabelCap)));
		AllWeapons = hashSet6.ToList();
		AllWeapons.Sort((ThingDef a, ThingDef b) => TaggedString.op_Implicit(((Def)a).LabelCap).CompareTo(TaggedString.op_Implicit(((Def)b).LabelCap)));
		AllTech = hashSet7.ToList();
		AllTech.Sort((ThingDef a, ThingDef b) => TaggedString.op_Implicit(((Def)a).LabelCap).CompareTo(TaggedString.op_Implicit(((Def)b).LabelCap)));
		AllInvItems = hashSet8.ToList();
		AllInvItems.Sort((ThingDef a, ThingDef b) => TaggedString.op_Implicit(((Def)a).LabelCap).CompareTo(TaggedString.op_Implicit(((Def)b).LabelCap)));
		AllHumanlikeRaces = hashSet5.ToList();
		AllHumanlikeRaces.Sort((ThingDef a, ThingDef b) => TaggedString.op_Implicit(((Def)a).LabelCap).CompareTo(TaggedString.op_Implicit(((Def)b).LabelCap)));
		AllAnimalKindDefs = hashSet9.ToList();
		AllAnimalKindDefs.Sort((PawnKindDef a, PawnKindDef b) => TaggedString.op_Implicit(((Def)a).LabelCap).CompareTo(TaggedString.op_Implicit(((Def)b).LabelCap)));
		AllBodyTypes = hashSet11.ToList();
		AllBodyTypes.Sort((BodyTypeDef a, BodyTypeDef b) => string.Compare(TaggedString.op_Implicit(((Def)a).LabelCap) ?? ((Def)a).defName, TaggedString.op_Implicit(((Def)b).LabelCap) ?? ((Def)b).defName, StringComparison.InvariantCulture));
		AllRulePackDefs = hashSet10.ToList();
		AllRulePackDefs.Sort((RulePackDef a, RulePackDef b) => string.Compare(((Def)a).defName, ((Def)b).defName, StringComparison.InvariantCulture));
		AllGeneDefs = hashSet12.ToList();
		AllGeneDefs.Sort((GeneDef a, GeneDef b) => string.Compare(TaggedString.op_Implicit(((Def)a).LabelCap) ?? ((Def)a).defName, TaggedString.op_Implicit(((Def)b).LabelCap) ?? ((Def)b).defName, StringComparison.InvariantCulture));
		HashSet<string> hashSet13 = new HashSet<string>(64);
		List<BackstoryDef> list = new List<BackstoryDef>(256);
		List<BackstoryDef> list2 = new List<BackstoryDef>(256);
		foreach (BackstoryDef item3 in DefDatabase<BackstoryDef>.AllDefsListForReading)
		{
			if (item3.spawnCategories != null)
			{
				foreach (string spawnCategory in item3.spawnCategories)
				{
					if (spawnCategory != null)
					{
						hashSet13.Add(spawnCategory);
					}
				}
			}
			if ((int)item3.slot == 0)
			{
				list.Add(item3);
			}
			else
			{
				list2.Add(item3);
			}
		}
		AllBackstoryCategories = hashSet13.ToList();
		AllBackstoryCategories.Sort();
		list.Sort((BackstoryDef a, BackstoryDef b) => string.Compare(BackstoryTab.BackstoryLabel(a), BackstoryTab.BackstoryLabel(b), StringComparison.InvariantCulture));
		list2.Sort((BackstoryDef a, BackstoryDef b) => string.Compare(BackstoryTab.BackstoryLabel(a), BackstoryTab.BackstoryLabel(b), StringComparison.InvariantCulture));
		AllChildhoodBackstories = list;
		AllAdulthoodBackstories = list2;
		AllBackstoryDefs = list.ToList();
		AllBackstoryDefs.AddRange(list2);
		AllTraitDegrees = DefDatabase<TraitDef>.AllDefsListForReading.SelectMany((TraitDef t) => t.degreeDatas.Select((TraitDegreeData d) => (t: t, degree: d.degree))).OrderBy(delegate((TraitDef t, int degree) x)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			TaggedString labelCap = ((Def)x.t).LabelCap;
			return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
		}).ThenBy(((TraitDef t, int degree) x) => x.degree)
			.ToList();
		PopulateVFEAncientsObjects();
	}

	private static void PopulateVFEAncientsObjects()
	{
		if (!VFEAncientsReflectionModule.ModLoaded.Value || !(VFEAncientsReflectionModule.GetPowerDefsMethod.Value?.GetValue(null) is IList list))
		{
			return;
		}
		AllPowerDefs = new List<string>();
		foreach (object item in list)
		{
			Def val = (Def)((item is Def) ? item : null);
			if (val != null)
			{
				AllPowerDefs.Add(val.defName);
			}
		}
		AllPowerDefs.Sort();
	}

	public static bool ApparelMaterialAllows(PawnKindDef kind, ThingDef stuff)
	{
		return MaterialAllows(ApparelMaterialCache, kind, stuff);
	}

	public static bool WeaponMaterialAllows(PawnKindDef kind, ThingDef stuff)
	{
		return MaterialAllows(WeaponMaterialCache, kind, stuff);
	}

	public static bool MaterialAllows(Dictionary<PawnKindDef, (HashSet<ThingDef> defs, bool blocklist)> cache, PawnKindDef kind, ThingDef stuff)
	{
		if (kind == null || stuff == null || !cache.TryGetValue(kind, out (HashSet<ThingDef>, bool) value))
		{
			return true;
		}
		bool flag = value.Item1.Contains(stuff);
		if (!value.Item2)
		{
			return flag;
		}
		return !flag;
	}

	public static string MaterialCategorySummary(List<DefRef<ThingDef>> materials, bool isBlocklist)
	{
		IEnumerable<ThingDef> enumerable;
		if (isBlocklist)
		{
			HashSet<ThingDef> banned = new HashSet<ThingDef>();
			if (materials != null)
			{
				foreach (DefRef<ThingDef> material in materials)
				{
					if (material.HasValue)
					{
						banned.Add(material.Def);
					}
				}
			}
			enumerable = GenStuff.StuffDefs.Where((ThingDef s) => !banned.Contains(s));
		}
		else
		{
			enumerable = from r in materials ?? Enumerable.Empty<DefRef<ThingDef>>()
				where r.HasValue
				select r.Def;
		}
		Dictionary<StuffCategoryDef, int> dictionary = new Dictionary<StuffCategoryDef, int>();
		foreach (ThingDef item in enumerable)
		{
			if (item?.stuffProps?.categories == null)
			{
				continue;
			}
			foreach (StuffCategoryDef category in item.stuffProps.categories)
			{
				dictionary.TryGetValue(category, out var value);
				dictionary[category] = value + 1;
			}
		}
		if (dictionary.Count != 0)
		{
			return string.Join("   ", from kv in dictionary
				orderby kv.Value descending
				select $"{((Def)kv.Key).LabelCap}: {kv.Value}");
		}
		return null;
	}

	public static void BuildBlacklistCaches(PawnKindEdit edit, PawnKindDef def, PawnKindEdit global)
	{
		IEnumerable<DefRef<ThingDef>> enumerable = global?.ApparelBlacklist;
		HashSet<ThingDef> hashSet = (from r in GenCollection.ConcatIfNotNull<DefRef<ThingDef>>(enumerable ?? Enumerable.Empty<DefRef<ThingDef>>(), (IEnumerable<DefRef<ThingDef>>)edit.ApparelBlacklist)
			where r.HasValue
			select r.Def).ToHashSet();
		if (hashSet.Count > 0)
		{
			ApparelBlacklistCache[def] = hashSet;
		}
		else
		{
			ApparelBlacklistCache.Remove(def);
		}
		enumerable = global?.WeaponBlacklist;
		HashSet<ThingDef> hashSet2 = (from r in GenCollection.ConcatIfNotNull<DefRef<ThingDef>>(enumerable ?? Enumerable.Empty<DefRef<ThingDef>>(), (IEnumerable<DefRef<ThingDef>>)edit.WeaponBlacklist)
			where r.HasValue
			select r.Def).ToHashSet();
		if (hashSet2.Count > 0)
		{
			WeaponBlacklistCache[def] = hashSet2;
		}
		else
		{
			WeaponBlacklistCache.Remove(def);
		}
		List<DefRef<ThingDef>> obj = edit.ApparelMaterials ?? global?.ApparelMaterials;
		bool item = ((edit.ApparelMaterials != null) ? edit.ApparelMaterialsBlocklist : (global?.ApparelMaterialsBlocklist ?? false));
		HashSet<ThingDef> hashSet3 = (from r in obj?.Where((DefRef<ThingDef> r) => r.HasValue)
			select r.Def).ToHashSet();
		if (hashSet3 != null && hashSet3.Count > 0)
		{
			ApparelMaterialCache[def] = (hashSet3, item);
		}
		else
		{
			ApparelMaterialCache.Remove(def);
		}
		List<DefRef<ThingDef>> obj2 = edit.WeaponMaterials ?? global?.WeaponMaterials;
		bool item2 = ((edit.WeaponMaterials != null) ? edit.WeaponMaterialsBlocklist : (global?.WeaponMaterialsBlocklist ?? false));
		HashSet<ThingDef> hashSet4 = (from r in obj2?.Where((DefRef<ThingDef> r) => r.HasValue)
			select r.Def).ToHashSet();
		if (hashSet4 != null && hashSet4.Count > 0)
		{
			WeaponMaterialCache[def] = (hashSet4, item2);
		}
		else
		{
			WeaponMaterialCache.Remove(def);
		}
	}
}
