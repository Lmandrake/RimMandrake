using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Modules;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public static class PawnKindApplicator
{
	public static PawnKindDef Apply(PawnKindEdit edit, PawnKindDef def, PawnKindEdit global, bool addToEdits = true)
	{
		//IL_0530: Unknown result type (might be due to invalid IL or missing references)
		//IL_0535: Unknown result type (might be due to invalid IL or missing references)
		//IL_0545: Unknown result type (might be due to invalid IL or missing references)
		//IL_054a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0569: Unknown result type (might be due to invalid IL or missing references)
		//IL_061d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0622: Unknown result type (might be due to invalid IL or missing references)
		//IL_0634: Unknown result type (might be due to invalid IL or missing references)
		//IL_0650: Expected O, but got Unknown
		//IL_09c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_09d3: Expected O, but got Unknown
		//IL_0a4e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a58: Expected O, but got Unknown
		if (def == null)
		{
			return null;
		}
		if (addToEdits)
		{
			PawnKindEdit.AddActiveEdit(def, edit);
			DefCache.BuildBlacklistCaches(edit, def, global);
		}
		if (edit.ReplaceWith != null)
		{
			return edit.ReplaceWith;
		}
		if (def.RaceProps.Animal)
		{
			edit.Race = null;
		}
		ReplaceUtils.ReplaceMaybe<QualityCategory>(ref def.itemQuality, edit.ItemQuality);
		ReplaceUtils.ReplaceMaybe(ref def.biocodeWeaponChance, edit.BiocodeWeaponChance);
		ReplaceUtils.ReplaceMaybe(ref def.techHediffsChance, edit.TechHediffChance);
		ReplaceUtils.ReplaceMaybe(ref def.techHediffsMaxAmount, edit.TechHediffsMaxAmount);
		ReplaceUtils.ReplaceMaybe<FloatRange>(ref def.apparelMoney, edit.ApparelMoney);
		ReplaceUtils.ReplaceMaybe<FloatRange>(ref def.techHediffsMoney, edit.TechMoney);
		ReplaceUtils.ReplaceMaybe<FloatRange>(ref def.weaponMoney, edit.WeaponMoney);
		ReplaceUtils.ReplaceMaybe(ref def.minGenerationAge, edit.MinGenerationAge);
		ReplaceUtils.ReplaceMaybe(ref def.maxGenerationAge, edit.MaxGenerationAge);
		ReplaceUtils.ReplaceMaybe(ref def.inventoryOptions, edit.Inventory, edit, global);
		ReplaceUtils.ReplaceMaybe<QualityCategory>(ref def.forceWeaponQuality, edit.ForcedWeaponQuality);
		ReplaceUtils.ReplaceMaybe(ref ((Def)def).label, edit.Label);
		ReplaceUtils.ReplaceMaybe(ref def.race, edit.Race);
		ReplaceUtils.ReplaceMaybe<Gender>(ref def.fixedGender, edit.ForcedGender);
		ReplaceUtils.ReplaceMaybe(ref def.nameMaker, edit.NameMaker);
		ReplaceUtils.ReplaceMaybe(ref def.nameMakerFemale, edit.NameMakerFemale);
		ReplaceUtils.ReplaceMaybe(ref def.combatPower, edit.CombatPower);
		ReplaceUtils.ReplaceMaybe(ref def.appearsRandomlyInCombatGroups, edit.AppearsRandomlyInCombatGroups);
		ReplaceUtils.ReplaceMaybeList(ref def.techHediffsTags, edit.TechHediffTags, global?.TechHediffTags != null);
		ReplaceUtils.ReplaceMaybeList(ref def.techHediffsDisallowTags, edit.TechHediffDisallowedTags, global?.TechHediffDisallowedTags != null);
		ReplaceUtils.ReplaceMaybeList(ref def.weaponTags, edit.WeaponTags, global?.WeaponTags != null);
		ReplaceUtils.ReplaceMaybeList(ref def.apparelTags, edit.ApparelTags, global?.ApparelTags != null);
		ReplaceUtils.ReplaceMaybeList(ref def.apparelDisallowTags, edit.ApparelDisallowedTags, global?.ApparelDisallowedTags != null);
		ReplaceUtils.ReplaceMaybeDefRefList<ThingDef>(ref def.apparelRequired, edit.ApparelRequired, global?.ApparelRequired != null);
		ReplaceUtils.ReplaceMaybeDefRefList<ThingDef>(ref def.techHediffsRequired, edit.TechRequired, global?.TechRequired != null);
		List<BackstoryFilter> backstoryFiltersOverride = edit.BackstoryFiltersOverride;
		PawnKindDef val;
		if (backstoryFiltersOverride != null && backstoryFiltersOverride.Count > 0)
		{
			val = def;
			List<BackstoryFilter> backstoryFiltersOverride2 = edit.BackstoryFiltersOverride;
			List<BackstoryCategoryFilter> list = new List<BackstoryCategoryFilter>(backstoryFiltersOverride2.Count);
			foreach (BackstoryFilter item in backstoryFiltersOverride2)
			{
				list.Add((BackstoryCategoryFilter)(object)item);
			}
			val.backstoryFiltersOverride = list;
		}
		ReplaceUtils.ReplaceMaybe(ref def.backstoryCryptosleepCommonality, edit.BackstoryCryptosleepCommonality);
		ReplaceUtils.ReplaceMaybeDefRefList<BackstoryDef>(ref def.fixedChildBackstories, edit.FixedChildBackstories, global?.FixedChildBackstories != null);
		ReplaceUtils.ReplaceMaybeDefRefList<BackstoryDef>(ref def.fixedAdultBackstories, edit.FixedAdultBackstories, global?.FixedAdultBackstories != null);
		ApplyBackstoryExclusions(edit, def);
		if (edit.RemoveFixedInventory || (global != null && global.RemoveFixedInventory))
		{
			def.fixedInventory = new List<ThingDefCountClass>();
		}
		if (edit.ApparelRequired != null || edit.SpecificApparel != null)
		{
			def.specificApparelRequirements = null;
		}
		if (edit.Race != null)
		{
			PawnKindDef val2 = GenCollection.FirstOrDefault<PawnKindDef>(DefDatabase<PawnKindDef>.AllDefsListForReading, (Predicate<PawnKindDef>)((PawnKindDef k) => k != def && ((Def)k).defName != ((Def)def).defName && k.race == edit.Race));
			if (val2 != null)
			{
				def.lifeStages = val2.lifeStages;
			}
		}
		Color? val3 = edit.ApparelColor;
		if (val3.HasValue)
		{
			Color? val4 = val3;
			Color white = Color.white;
			if (val4.HasValue && val4.GetValueOrDefault() == white)
			{
				val3 = new Color(0.995f, 0.995f, 0.995f, 1f);
			}
		}
		ReplaceUtils.ReplaceMaybe<Color>(ref def.apparelColor, val3);
		if (!def.RaceProps.Animal && edit.ForcedTraitsDef != null)
		{
			def.forcedTraits = new List<TraitRequirement>();
			foreach (ForcedTrait t in edit.ForcedTraitsDef)
			{
				if (t.TraitDef != null && !GenCollection.Any<TraitRequirement>(def.forcedTraits, (Predicate<TraitRequirement>)((TraitRequirement e) => e.def == t.TraitDef && e.degree.GetValueOrDefault() == t.degree)))
				{
					def.forcedTraits.Add(new TraitRequirement
					{
						def = t.TraitDef,
						degree = t.degree
					});
				}
			}
		}
		val = def;
		if (((Def)val).modExtensions == null)
		{
			((Def)val).modExtensions = new List<DefModExtension>();
		}
		ForcedExtrasModExtension forcedExtrasModExtension = null;
		List<ForcedHediff> forcedHediffs = edit.ForcedHediffs;
		if (forcedHediffs != null && forcedHediffs.Count > 0)
		{
			forcedExtrasModExtension = ((Def)def).GetModExtension<ForcedExtrasModExtension>() ?? ((Def)def).GetModExtension<ForcedHediffModExtension>();
			if (forcedExtrasModExtension == null)
			{
				forcedExtrasModExtension = new ForcedExtrasModExtension();
				((Def)def).modExtensions.Add((DefModExtension)(object)forcedExtrasModExtension);
			}
			forcedExtrasModExtension.forcedHediffs.AddRange(edit.ForcedHediffs);
			List<ForcedHediff> forcedHediffs2 = forcedExtrasModExtension.forcedHediffs;
			ModCore.Debug("Adding forced hediffs " + (((forcedHediffs2 != null) ? GenText.ToCommaList(forcedHediffs2.Select((ForcedHediff h) => ((Def)(h.HediffDef?)).defName), false, false) : null) ?? "None") + " to " + ((Def)def).defName);
		}
		List<ForcedGene> forcedGenes = edit.ForcedGenes;
		if (forcedGenes != null && forcedGenes.Count > 0)
		{
			if (forcedExtrasModExtension == null)
			{
				forcedExtrasModExtension = ((Def)def).GetModExtension<ForcedExtrasModExtension>();
			}
			if (forcedExtrasModExtension == null)
			{
				forcedExtrasModExtension = new ForcedExtrasModExtension();
				((Def)def).modExtensions.Add((DefModExtension)(object)forcedExtrasModExtension);
			}
			forcedExtrasModExtension.forcedGenes.AddRange(edit.ForcedGenes);
			List<ForcedGene> forcedGenes2 = forcedExtrasModExtension.forcedGenes;
			ModCore.Debug("Adding forced genes " + (((forcedGenes2 != null) ? GenText.ToCommaList(forcedGenes2.Select((ForcedGene h) => ((Def)(h.GeneDef?)).defName), false, false) : null) ?? "None") + " to " + ((Def)def).defName);
		}
		if (!def.RaceProps.Animal)
		{
			List<ForcedTrait> forcedTraits = edit.ForcedTraits;
			if (forcedTraits != null && forcedTraits.Count > 0)
			{
				if (def.forcedTraits != null)
				{
					foreach (ForcedTrait t2 in edit.ForcedTraits)
					{
						if (t2.TraitDef != null)
						{
							def.forcedTraits.RemoveAll((TraitRequirement e) => e.def == t2.TraitDef && e.degree.GetValueOrDefault() == t2.degree);
						}
					}
				}
				if (forcedExtrasModExtension == null)
				{
					forcedExtrasModExtension = ((Def)def).GetModExtension<ForcedExtrasModExtension>();
				}
				if (forcedExtrasModExtension == null)
				{
					forcedExtrasModExtension = new ForcedExtrasModExtension();
					((Def)def).modExtensions.Add((DefModExtension)(object)forcedExtrasModExtension);
				}
				foreach (ForcedTrait t3 in edit.ForcedTraits)
				{
					forcedExtrasModExtension.forcedTraits.RemoveAll((ForcedTrait e) => e.traitDef == t3.traitDef && e.degree == t3.degree);
					forcedExtrasModExtension.forcedTraits.Add(t3);
				}
			}
		}
		if (ModsConfig.BiotechActive && def.RaceProps.Humanlike && edit.ForceSpecificXenos && (edit.ForcedXenotypeChanceDefs?.Count ?? 0) >= 1)
		{
			def.useFactionXenotypes = false;
			val = def;
			if (val.xenotypeSet == null)
			{
				val.xenotypeSet = new XenotypeSet();
			}
			XenotypeSet xenotypeSet = def.xenotypeSet;
			if (xenotypeSet.xenotypeChances == null)
			{
				xenotypeSet.xenotypeChances = new List<XenotypeChance>();
			}
			def.xenotypeSet.xenotypeChances.Clear();
			foreach (KeyValuePair<XenotypeDef, float> item2 in edit.ForcedXenotypeChanceDefs ?? new Dictionary<XenotypeDef, float>())
			{
				def.xenotypeSet.xenotypeChances.Add(new XenotypeChance(item2.Key, item2.Value));
			}
		}
		if (def.RaceProps.Animal)
		{
			return def;
		}
		VFEAncientsReflectionModule.ApplyVFEAncientsEdits(edit, def);
		VEPsycastsReflectionModule.ApplyVEPsycastsEdits(edit, def);
		foreach (ITotalControlModule module in ModuleRegistry.Modules)
		{
			if (module.IsActive)
			{
				try
				{
					module.Apply(edit, def, global);
				}
				catch (Exception e2)
				{
					ModCore.Error("Error applying module '" + module.ModuleName + "' (key: " + module.ModuleKey + ") to " + ((Def)def).defName, e2);
				}
			}
		}
		return def;
	}

	private static void ApplyBackstoryExclusions(PawnKindEdit edit, PawnKindDef def)
	{
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Invalid comparison between Unknown and I4
		List<string> excludedBackstoryCategories = edit.ExcludedBackstoryCategories;
		bool num = excludedBackstoryCategories != null && excludedBackstoryCategories.Count > 0;
		List<DefRef<BackstoryDef>> excludedBackstories = edit.ExcludedBackstories;
		bool flag = excludedBackstories != null && excludedBackstories.Count > 0;
		if (num)
		{
			InjectExcludes(def.backstoryFiltersOverride);
			InjectExcludes(def.backstoryFilters);
		}
		if (!flag)
		{
			return;
		}
		HashSet<BackstoryDef> excludedChild = new HashSet<BackstoryDef>();
		HashSet<BackstoryDef> excludedAdult = new HashSet<BackstoryDef>();
		foreach (DefRef<BackstoryDef> excludedBackstory in edit.ExcludedBackstories)
		{
			BackstorySlot? val = excludedBackstory?.Def?.slot;
			if (!val.HasValue)
			{
				continue;
			}
			BackstorySlot valueOrDefault = val.GetValueOrDefault();
			if ((int)valueOrDefault != 0)
			{
				if ((int)valueOrDefault == 1)
				{
					excludedAdult.Add(excludedBackstory.Def);
				}
			}
			else
			{
				excludedChild.Add(excludedBackstory.Def);
			}
		}
		if (excludedChild.Count > 0)
		{
			def.fixedChildBackstories?.RemoveAll((BackstoryDef b) => excludedChild.Contains(b));
		}
		if (excludedAdult.Count > 0)
		{
			def.fixedAdultBackstories?.RemoveAll((BackstoryDef b) => excludedAdult.Contains(b));
		}
		HashSet<string> hashSet = new HashSet<string>();
		HashSet<string> hashSet2 = new HashSet<string>();
		List<BackstoryCategoryFilter> list = def.backstoryFiltersOverride ?? def.backstoryFilters;
		if (list != null)
		{
			foreach (BackstoryCategoryFilter item in list)
			{
				if (!GenList.NullOrEmpty<string>((IList<string>)item.categories))
				{
					foreach (string category in item.categories)
					{
						hashSet.Add(category);
						hashSet2.Add(category);
					}
				}
				if (!GenList.NullOrEmpty<string>((IList<string>)item.categoriesChildhood))
				{
					foreach (string item2 in item.categoriesChildhood)
					{
						hashSet.Add(item2);
					}
				}
				if (GenList.NullOrEmpty<string>((IList<string>)item.categoriesAdulthood))
				{
					continue;
				}
				foreach (string item3 in item.categoriesAdulthood)
				{
					hashSet2.Add(item3);
				}
			}
		}
		if (excludedChild.Count > 0)
		{
			ResolveBackstoryCategories(def, (BackstorySlot)0, hashSet, excludedChild);
		}
		if (excludedAdult.Count > 0)
		{
			ResolveBackstoryCategories(def, (BackstorySlot)1, hashSet2, excludedAdult);
		}
		void InjectExcludes(List<BackstoryCategoryFilter> filters)
		{
			if (filters == null)
			{
				return;
			}
			foreach (BackstoryCategoryFilter filter in filters)
			{
				BackstoryCategoryFilter val2 = filter;
				if (val2.exclude == null)
				{
					val2.exclude = new List<string>();
				}
				foreach (string excludedBackstoryCategory in edit.ExcludedBackstoryCategories)
				{
					if (!filter.exclude.Contains(excludedBackstoryCategory))
					{
						filter.exclude.Add(excludedBackstoryCategory);
					}
				}
			}
		}
	}

	private static void ResolveBackstoryCategories(PawnKindDef def, BackstorySlot slot, HashSet<string> categories, HashSet<BackstoryDef> excluded)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Invalid comparison between Unknown and I4
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		List<BackstoryDef> list = (((int)slot == 0) ? def.fixedChildBackstories : def.fixedAdultBackstories);
		HashSet<BackstoryDef> hashSet2;
		if (list != null)
		{
			HashSet<BackstoryDef> hashSet = new HashSet<BackstoryDef>();
			foreach (BackstoryDef item in list)
			{
				hashSet.Add(item);
			}
			hashSet2 = hashSet;
		}
		else
		{
			hashSet2 = new HashSet<BackstoryDef>();
		}
		HashSet<BackstoryDef> existing = hashSet2;
		List<BackstoryDef> list2 = (from bs in DefDatabase<BackstoryDef>.AllDefsListForReading
			where bs.slot == slot && bs.shuffleable && !excluded.Contains(bs) && !existing.Contains(bs)
			where bs.spawnCategories != null
			where categories.Count <= 0 || GenCollection.Any<string>(bs.spawnCategories, (Predicate<string>)categories.Contains)
			select bs).ToList();
		BackstorySlot val = slot;
		if ((int)val != 0)
		{
			if ((int)val != 1)
			{
				return;
			}
			PawnKindDef val2 = def;
			if (val2.fixedAdultBackstories == null)
			{
				val2.fixedAdultBackstories = new List<BackstoryDef>();
			}
			def.fixedAdultBackstories.AddRange(list2);
		}
		else
		{
			PawnKindDef val2 = def;
			if (val2.fixedChildBackstories == null)
			{
				val2.fixedChildBackstories = new List<BackstoryDef>();
			}
			def.fixedChildBackstories.AddRange(list2);
		}
		ModCore.Debug($"Backstory exclusions for {((Def)def).defName} ({slot}): {excluded.Count} excluded, {list2.Count} resolved from categories into fixed list.");
	}
}
