using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Xml;
using FactionLoadout.Modules;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class PawnKindEdit : IExposable
{
	public static Dictionary<PawnKindDef, List<PawnKindEdit>> activeEdits = new Dictionary<PawnKindDef, List<PawnKindEdit>>();

	public static Dictionary<PawnKindDef, PawnKindDef> replacementToOriginal = new Dictionary<PawnKindDef, PawnKindDef>();

	[NoCopy]
	public PawnKindDef Def;

	[NoCopy]
	public bool IsGlobal;

	[NoCopy]
	public bool DeletedOrClosed;

	[NoCopy]
	public PawnKindEdit globalEdit;

	[NoCopy]
	public Dictionary<string, string> preservedModuleXml;

	public PawnKindDef ReplaceWith;

	public bool RenameDef;

	public bool ForceNaked;

	public bool ForceOnlySelected;

	public bool ForceSpecificXenos;

	public QualityCategory? ItemQuality;

	public float? BiocodeWeaponChance;

	public float? TechHediffChance;

	public int? TechHediffsMaxAmount;

	public int? MinGenerationAge;

	public int? MaxGenerationAge;

	public List<string> TechHediffTags;

	public List<string> TechHediffDisallowedTags;

	public List<string> WeaponTags;

	public List<string> ApparelTags;

	public List<string> ApparelDisallowedTags;

	public List<DefRef<ThingDef>> ApparelBlacklist;

	public List<DefRef<ThingDef>> WeaponBlacklist;

	public List<DefRef<ThingDef>> ApparelMaterials;

	public bool ApparelMaterialsBlocklist;

	public List<DefRef<ThingDef>> WeaponMaterials;

	public bool WeaponMaterialsBlocklist;

	public List<DefRef<ThingDef>> ApparelRequired;

	public List<DefRef<ThingDef>> TechRequired;

	public List<SpecRequirementEdit> SpecificApparel;

	public List<SpecRequirementEdit> SpecificWeapons;

	public FloatRange? ApparelMoney;

	public FloatRange? TechMoney;

	public FloatRange? WeaponMoney;

	public InventoryOptionEdit Inventory;

	public bool ReplaceDefaultInventory = true;

	public bool RemoveFixedInventory;

	public QualityCategory? ForcedWeaponQuality;

	public Color? ApparelColor;

	public string Label;

	public ThingDef Race;

	public List<DefRef<HairDef>> CustomHair;

	public List<DefRef<BeardDef>> CustomBeards;

	public List<DefRef<BodyTypeDef>> BodyTypes;

	public List<DefRef<TattooDef>> CustomFaceTattoos;

	public List<DefRef<TattooDef>> CustomBodyTattoos;

	public List<Color> CustomHairColors;

	public List<ForcedHediff> ForcedHediffs;

	public List<ForcedGene> ForcedGenes;

	public List<ForcedTrait> ForcedTraitsDef;

	public List<ForcedTrait> ForcedTraits;

	public Dictionary<string, float> ForcedXenotypeChances = new Dictionary<string, float>();

	public Dictionary<XenotypeDef, float> ForcedXenotypeChanceDefs = new Dictionary<XenotypeDef, float>();

	public Gender? ForcedGender;

	public string ForcedIdeoKey;

	public ForcedIdeoSource ForcedIdeoSourceKind;

	public SimpleCurve RaidCommonalityFromPointsCurve;

	public SimpleCurve RaidLootValueFromPointsCurve;

	public SimpleCurve MaxPawnCostPerTotalPointsCurve;

	public RulePackDef NameMaker;

	public RulePackDef NameMakerFemale;

	public float? UnwaveringlyLoyalChance;

	public float? CombatPower;

	public bool? AppearsRandomlyInCombatGroups;

	public List<BackstoryFilter> BackstoryFiltersOverride;

	public List<DefRef<BackstoryDef>> FixedChildBackstories;

	public List<DefRef<BackstoryDef>> FixedAdultBackstories;

	public List<string> ExcludedBackstoryCategories;

	public List<DefRef<BackstoryDef>> ExcludedBackstories;

	public float? BackstoryCryptosleepCommonality;

	public int? NumVFEAncientsSuperPowers;

	public int? NumVFEAncientsSuperWeaknesses;

	public List<string> ForcedVFEAncientsItems;

	public int? VEPsycastLevel;

	public IntRange? VEPsycastStatPoints;

	public bool? VEPsycastRandomAbilities;

	public static readonly FieldInfo[] CopyableFields = (from f in typeof(PawnKindEdit).GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
		where f.GetCustomAttribute<NoCopyAttribute>() == null
		select f).ToArray();

	public FactionEdit ParentEdit => Preset.LoadedPresets.SelectMany((Preset preset) => preset.factionChanges).FirstOrDefault((FactionEdit change) => change.KindEdits.Contains(this));

	public static void RecordReplacement(PawnKindDef original, PawnKindDef replacement)
	{
		GenCollection.SetOrAdd<PawnKindDef, PawnKindDef>(replacementToOriginal, replacement, original);
	}

	public static List<PawnKindEdit> RemoveActiveEdits(PawnKindDef pawnKindDef)
	{
		List<PawnKindEdit> result = GenCollection.TryGetValue<PawnKindDef, List<PawnKindEdit>>((IReadOnlyDictionary<PawnKindDef, List<PawnKindEdit>>)activeEdits, pawnKindDef, (List<PawnKindEdit>)null);
		activeEdits.Remove(pawnKindDef);
		return result;
	}

	public static void SetActiveEdits(PawnKindDef pawnKindDef, List<PawnKindEdit> edits)
	{
		GenCollection.SetOrAdd<PawnKindDef, List<PawnKindEdit>>(activeEdits, pawnKindDef, edits);
	}

	public static PawnKindDef NormaliseDef(PawnKindDef def)
	{
		if (def == null)
		{
			return null;
		}
		if (!replacementToOriginal.TryGetValue(def, out var value))
		{
			return def;
		}
		return value ?? def;
	}

	public static IEnumerable<PawnKindEdit> GetEditsFor(PawnKindDef def, FactionDef factionDef)
	{
		if (def == null)
		{
			yield break;
		}
		factionDef = ForcedFactionForEditing(def, factionDef);
		if (!activeEdits.TryGetValue(def, out var value))
		{
			yield break;
		}
		foreach (PawnKindEdit item in value)
		{
			if (factionDef == null || item.ParentEdit.Faction.Def == factionDef || FactionEdit.TryGetOriginal(((Def)factionDef).defName) == item.ParentEdit.Faction.Def || (factionDef.fixedName?.StartsWith("TEMP FACTION CLONE") ?? false))
			{
				yield return item;
			}
		}
	}

	public static FactionDef ForcedFactionForEditing(PawnKindDef def, FactionDef fallbackFactionDef)
	{
		if (def == null)
		{
			return fallbackFactionDef;
		}
		if (def == PawnKindDefOf.WildMan)
		{
			return Preset.SpecialWildManFaction;
		}
		if (def is CreepJoinerFormKindDef)
		{
			return Preset.SpecialCreepjoinerFaction;
		}
		if (fallbackFactionDef == null && Preset.FactionlessPawnKindsSet.Contains(def))
		{
			return Preset.SpecialFactionlessPawnsFaction;
		}
		return fallbackFactionDef;
	}

	public static void ClearState()
	{
		activeEdits.Clear();
		replacementToOriginal.Clear();
	}

	public static void AddActiveEdit(PawnKindDef def, PawnKindEdit edit)
	{
		if (def != null && edit != null)
		{
			if (!activeEdits.TryGetValue(def, out var value))
			{
				value = new List<PawnKindEdit>();
				activeEdits.Add(def, value);
			}
			if (!value.Contains(edit))
			{
				value.Add(edit);
			}
		}
	}

	public PawnKindEdit()
	{
	}

	public PawnKindEdit(PawnKindDef def)
	{
		Def = def;
	}

	public PawnKindDef Apply(PawnKindDef def, PawnKindEdit global, bool addToEdits = true)
	{
		globalEdit = global;
		try
		{
			return PawnKindApplicator.Apply(this, def, global, addToEdits);
		}
		finally
		{
			globalEdit = null;
		}
	}

	public void ExposeData()
	{
		//IL_04c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_04cd: Invalid comparison between Unknown and I4
		Scribe_Defs.Look<PawnKindDef>(ref Def, "def");
		Scribe_Defs.Look<PawnKindDef>(ref ReplaceWith, "replaceWith");
		Scribe_Values.Look<bool>(ref RemoveFixedInventory, "removeFixedInventory", false, false);
		Scribe_Values.Look<bool>(ref ForceNaked, "forceNaked", false, false);
		Scribe_Values.Look<bool>(ref RenameDef, "renameDef", false, false);
		Scribe_Values.Look<bool>(ref ForceOnlySelected, "forceOnlySelected", false, false);
		Scribe_Values.Look<bool>(ref ForceSpecificXenos, "forceSpecificXenos", false, false);
		Scribe_Values.Look<QualityCategory?>(ref ItemQuality, "itemQuality", (QualityCategory?)null, false);
		Scribe_Values.Look<float?>(ref TechHediffChance, "techHediffChance", (float?)null, false);
		Scribe_Values.Look<int?>(ref TechHediffsMaxAmount, "techHediffsMaxAmount", (int?)null, false);
		Scribe_Collections.Look<string>(ref TechHediffDisallowedTags, "techHediffDisallowedTags", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref TechHediffTags, "techHediffTags", (LookMode)0, Array.Empty<object>());
		Scribe_Values.Look<float?>(ref BiocodeWeaponChance, "biocodeWeaponChance", (float?)null, false);
		Scribe_Values.Look<FloatRange?>(ref ApparelMoney, "apparelMoney", (FloatRange?)null, false);
		Scribe_Values.Look<FloatRange?>(ref TechMoney, "techMoney", (FloatRange?)null, false);
		Scribe_Values.Look<FloatRange?>(ref WeaponMoney, "weaponMoney", (FloatRange?)null, false);
		Scribe_Values.Look<int?>(ref MinGenerationAge, "minGenerationAge", (int?)null, false);
		Scribe_Values.Look<int?>(ref MaxGenerationAge, "maxGenerationAge", (int?)null, false);
		Scribe_Collections.Look<string>(ref WeaponTags, "weaponTags", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref ApparelTags, "apparelTags", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref ApparelDisallowedTags, "apparelDisallowedTags", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<ThingDef>>(ref ApparelBlacklist, "apparelBlacklist", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<ThingDef>>(ref WeaponBlacklist, "weaponBlacklist", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<ThingDef>>(ref ApparelMaterials, "apparelMaterials", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<ThingDef>>(ref WeaponMaterials, "weaponMaterials", (LookMode)2, Array.Empty<object>());
		Scribe_Values.Look<bool>(ref ApparelMaterialsBlocklist, "apparelMaterialsBlocklist", false, false);
		Scribe_Values.Look<bool>(ref WeaponMaterialsBlocklist, "weaponMaterialsBlocklist", false, false);
		ScribeMigrateDefRefList<ThingDef>(ref ApparelRequired, "apparelRequired");
		ScribeMigrateDefRefList<ThingDef>(ref TechRequired, "techRequired");
		Scribe_Collections.Look<SpecRequirementEdit>(ref SpecificApparel, "specificApparel", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<SpecRequirementEdit>(ref SpecificWeapons, "specificWeapons", (LookMode)2, Array.Empty<object>());
		Scribe_Deep.Look<InventoryOptionEdit>(ref Inventory, "inventory", Array.Empty<object>());
		Scribe_Values.Look<bool>(ref IsGlobal, "isGlobal", false, false);
		Scribe_Values.Look<bool>(ref ReplaceDefaultInventory, "replaceDefaultInventory", false, false);
		Scribe_Values.Look<QualityCategory?>(ref ForcedWeaponQuality, "forcedWeaponQuality", (QualityCategory?)null, false);
		Scribe_Values.Look<Color?>(ref ApparelColor, "apparelColor", (Color?)null, false);
		Scribe_Values.Look<string>(ref Label, "label", (string)null, false);
		Scribe_Defs.Look<ThingDef>(ref Race, "race");
		Scribe_Values.Look<Gender?>(ref ForcedGender, "forcedGender", (Gender?)null, false);
		Scribe_Values.Look<string>(ref ForcedIdeoKey, "forcedIdeoKey", (string)null, false);
		Scribe_Values.Look<ForcedIdeoSource>(ref ForcedIdeoSourceKind, "forcedIdeoSourceKind", ForcedIdeoSource.SavedFile, false);
		ScribeMigrateDefRefList<BodyTypeDef>(ref BodyTypes, "bodyTypes");
		ScribeMigrateDefRefList<BeardDef>(ref CustomBeards, "customBeards");
		ScribeMigrateDefRefList<HairDef>(ref CustomHair, "customHair");
		ScribeMigrateDefRefList<TattooDef>(ref CustomFaceTattoos, "customFaceTattoos");
		ScribeMigrateDefRefList<TattooDef>(ref CustomBodyTattoos, "customBodyTattoos");
		Scribe_Collections.Look<Color>(ref CustomHairColors, "customHairColors", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<ForcedHediff>(ref ForcedHediffs, "forcedHediffs", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<ForcedGene>(ref ForcedGenes, "forcedGenes", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<ForcedTrait>(ref ForcedTraitsDef, "forcedTraitsDef", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<ForcedTrait>(ref ForcedTraits, "forcedTraits", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<string, float>(ref ForcedXenotypeChances, "forcedXenotypeChances", (LookMode)1, (LookMode)1);
		Scribe_Deep.Look<SimpleCurve>(ref RaidLootValueFromPointsCurve, "raidLootValueFromPointsCurve", Array.Empty<object>());
		Scribe_Deep.Look<SimpleCurve>(ref RaidCommonalityFromPointsCurve, "raidCommonalityFromPointsCurve", Array.Empty<object>());
		Scribe_Deep.Look<SimpleCurve>(ref MaxPawnCostPerTotalPointsCurve, "maxPawnCostPerTotalPointsCurve", Array.Empty<object>());
		Scribe_Values.Look<float?>(ref UnwaveringlyLoyalChance, "unwaveringlyLoyalChance", (float?)null, false);
		Scribe_Values.Look<float?>(ref CombatPower, "combatPower", (float?)null, false);
		Scribe_Values.Look<bool?>(ref AppearsRandomlyInCombatGroups, "appearsRandomlyInCombatGroups", (bool?)null, false);
		if ((int)Scribe.mode == 4)
		{
			if (ForcedXenotypeChances == null)
			{
				ForcedXenotypeChances = new Dictionary<string, float>();
			}
			ForcedXenotypeChanceDefs = (from kvp in ForcedXenotypeChances
				select (Def: DefDatabase<XenotypeDef>.GetNamedSilentFail(kvp.Key), Value: kvp.Value) into c
				where c.Def != null
				select c).ToDictionary(((XenotypeDef Def, float Value) c) => c.Def, ((XenotypeDef Def, float Value) c) => c.Value);
		}
		bool num = NameMaker == DefCache.FakeRulePack;
		if (num)
		{
			NameMaker = null;
		}
		Scribe_Defs.Look<RulePackDef>(ref NameMaker, "nameMaker");
		if (num)
		{
			NameMaker = DefCache.FakeRulePack;
		}
		bool num2 = NameMakerFemale == DefCache.FakeRulePack;
		if (num2)
		{
			NameMakerFemale = null;
		}
		Scribe_Defs.Look<RulePackDef>(ref NameMakerFemale, "nameMakerFemale");
		if (num2)
		{
			NameMakerFemale = DefCache.FakeRulePack;
		}
		Scribe_Collections.Look<BackstoryFilter>(ref BackstoryFiltersOverride, "backstoryFiltersOverride", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<BackstoryDef>>(ref FixedChildBackstories, "fixedChildBackstories", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<BackstoryDef>>(ref FixedAdultBackstories, "fixedAdultBackstories", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref ExcludedBackstoryCategories, "excludedBackstoryCategories", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<DefRef<BackstoryDef>>(ref ExcludedBackstories, "excludedBackstories", (LookMode)2, Array.Empty<object>());
		Scribe_Values.Look<float?>(ref BackstoryCryptosleepCommonality, "backstoryCryptosleepCommonality", (float?)null, false);
		Scribe_Values.Look<int?>(ref NumVFEAncientsSuperPowers, "numVFEAncientsSuperPowers", (int?)null, false);
		Scribe_Values.Look<int?>(ref NumVFEAncientsSuperWeaknesses, "numVFEAncientsSuperWeaknesses", (int?)null, false);
		Scribe_Collections.Look<string>(ref ForcedVFEAncientsItems, "forcedVFEAncientsEffects", (LookMode)0, Array.Empty<object>());
		Scribe_Values.Look<int?>(ref VEPsycastLevel, "vePsycastLevel", (int?)null, false);
		Scribe_Values.Look<IntRange?>(ref VEPsycastStatPoints, "vePsycastStatPoints", (IntRange?)null, false);
		Scribe_Values.Look<bool?>(ref VEPsycastRandomAbilities, "vePsycastRandomAbilities", (bool?)null, false);
		ExposeModuleData();
	}

	private void ExposeModuleData()
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Invalid comparison between Unknown and I4
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Invalid comparison between Unknown and I4
		//IL_032b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0331: Invalid comparison between Unknown and I4
		IReadOnlyList<ITotalControlModule> modules = ModuleRegistry.Modules;
		if ((int)Scribe.mode == 2)
		{
			XmlNode xmlNode = Scribe.loader.curXmlParent?["modules"];
			if (xmlNode == null)
			{
				return;
			}
			{
				foreach (XmlNode childNode in xmlNode.ChildNodes)
				{
					ITotalControlModule module = ModuleRegistry.GetModule(childNode.Name);
					if (module != null && module.IsActive)
					{
						XmlNode curXmlParent = Scribe.loader.curXmlParent;
						Scribe.loader.curXmlParent = childNode;
						try
						{
							module.ExposeData(this);
						}
						catch (Exception e)
						{
							ModCore.Error("Error loading module data for '" + module.ModuleName + "' (key: " + module.ModuleKey + ")", e);
						}
						Scribe.loader.curXmlParent = curXmlParent;
					}
					else
					{
						if (preservedModuleXml == null)
						{
							preservedModuleXml = new Dictionary<string, string>();
						}
						preservedModuleXml[childNode.Name] = childNode.InnerXml;
						ModCore.Debug("Preserving module data for absent module '" + childNode.Name + "'");
					}
				}
				return;
			}
		}
		if ((int)Scribe.mode == 1)
		{
			bool num = modules.Any((ITotalControlModule m) => m.IsActive);
			Dictionary<string, string> dictionary = preservedModuleXml;
			bool flag = dictionary != null && dictionary.Count > 0;
			if (!num && !flag)
			{
				return;
			}
			Scribe.saver.EnterNode("modules");
			try
			{
				foreach (ITotalControlModule item in modules)
				{
					if (item.IsActive)
					{
						Scribe.saver.EnterNode(item.ModuleKey);
						try
						{
							item.ExposeData(this);
						}
						catch (Exception e2)
						{
							ModCore.Error("Error saving module data for '" + item.ModuleName + "' (key: " + item.ModuleKey + ")", e2);
						}
						Scribe.saver.ExitNode();
					}
				}
				if (preservedModuleXml == null)
				{
					return;
				}
				HashSet<string> hashSet = new HashSet<string>(from m in modules
					where m.IsActive
					select m.ModuleKey);
				foreach (KeyValuePair<string, string> item2 in preservedModuleXml)
				{
					if (!hashSet.Contains(item2.Key))
					{
						Scribe.saver.writer.WriteStartElement(item2.Key);
						Scribe.saver.writer.WriteRaw(item2.Value);
						Scribe.saver.writer.WriteEndElement();
					}
				}
				return;
			}
			finally
			{
				Scribe.saver.ExitNode();
			}
		}
		if ((int)Scribe.mode != 4)
		{
			return;
		}
		foreach (ITotalControlModule item3 in modules)
		{
			if (item3.IsActive)
			{
				try
				{
					item3.ExposeData(this);
				}
				catch (Exception e3)
				{
					ModCore.Error("Error in post-load init for module '" + item3.ModuleName + "' (key: " + item3.ModuleKey + ")", e3);
				}
			}
		}
	}

	public void CopyFrom(PawnKindEdit source)
	{
		FieldInfo[] copyableFields = CopyableFields;
		foreach (FieldInfo fieldInfo in copyableFields)
		{
			fieldInfo.SetValue(this, DeepCopy.Value(fieldInfo.GetValue(source), fieldInfo.FieldType));
		}
		CopyModuleData(source, this);
	}

	public static void CopyModuleData(PawnKindEdit source, PawnKindEdit dest)
	{
		dest.preservedModuleXml = ((source.preservedModuleXml != null) ? new Dictionary<string, string>(source.preservedModuleXml) : null);
		foreach (ITotalControlModule module in ModuleRegistry.Modules)
		{
			if (module.IsActive)
			{
				try
				{
					module.CopyData(source, dest);
				}
				catch (Exception e)
				{
					ModCore.Error("Error copying module data for '" + module.ModuleName + "' (key: " + module.ModuleKey + ")", e);
				}
			}
		}
	}

	private static void ScribeMigrateDefRefList<T>(ref List<DefRef<T>> field, string xmlKey) where T : Def, new()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Invalid comparison between Unknown and I4
		if ((int)Scribe.mode == 2 && IsDefListOldFormat(Scribe.loader.curXmlParent?[xmlKey]))
		{
			List<T> list = null;
			Scribe_Collections.Look<T>(ref list, xmlKey, (LookMode)4, Array.Empty<object>());
			field = (from d in list?.Where((T d) => d != null)
				select new DefRef<T>(d)).ToList();
		}
		else
		{
			Scribe_Collections.Look<DefRef<T>>(ref field, xmlKey, (LookMode)2, Array.Empty<object>());
		}
	}

	private static bool IsDefListOldFormat(XmlNode collectionNode)
	{
		if (collectionNode != null && collectionNode.HasChildNodes)
		{
			return collectionNode.SelectSingleNode("li/defName") == null;
		}
		return false;
	}

	public bool AppliesTo(PawnKindDef def)
	{
		try
		{
			if (Def == null)
			{
				return false;
			}
			return def != null && (((Def)Def).defName == ((Def)def).defName || ((Def)def).defName == ((Def)NormaliseDef(Def)).defName);
		}
		catch (Exception)
		{
			Log.Message("Something was null when checking if edit for " + (((Def)(Def?)).defName ?? "UNKNOWN") + " applies to " + (((Def)(def?)).defName ?? "UNKNOWN"));
			throw;
		}
	}
}
