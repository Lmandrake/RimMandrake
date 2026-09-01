using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using FactionLoadout.Modules;
using FactionLoadout.Util;
using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout;

[HotSwappable]
public class FactionEdit : IExposable
{
	private static readonly Dictionary<string, FactionDef> originalFactionDefs = new Dictionary<string, FactionDef>();

	private static Dictionary<(FactionDef, PawnKindDef), PawnKindDef> factionSpecificPawnKindReplacements = new Dictionary<(FactionDef, PawnKindDef), PawnKindDef>();

	public static readonly Dictionary<string, FactionEdit> ActiveFactionEdits = new Dictionary<string, FactionEdit>();

	public bool Active = true;

	public ThingFilter ApparelStuffFilter;

	public TechLevel? TechLevel;

	public DefRef<PawnKindDef> BasicMemberKind = new DefRef<PawnKindDef>();

	public bool DeletedOrClosed;

	private Dictionary<string, string> preservedFactionModuleXml;

	public DefRef<FactionDef> Faction = new DefRef<FactionDef>();

	public string ForcedPrimaryIdeoKey;

	public ForcedIdeoSource ForcedPrimaryIdeoSourceKind;

	public List<PawnKindEdit> KindEdits = new List<PawnKindEdit>();

	public List<PawnGroupMakerEdit> PawnGroupMakerEdits;

	public Dictionary<string, float> xenotypeChances = new Dictionary<string, float>();

	public Dictionary<XenotypeDef, float> xenotypeChancesByDef = new Dictionary<XenotypeDef, float>();

	public bool OverrideFactionXenotypes;

	public PawnKindDef EffectiveBasicMemberKind
	{
		get
		{
			DefRef<PawnKindDef> basicMemberKind = BasicMemberKind;
			if (basicMemberKind == null || !basicMemberKind.HasValue)
			{
				return Faction.Def?.basicMemberKind;
			}
			return BasicMemberKind.Def;
		}
	}

	public static FactionEdit GetActiveEditFor(FactionDef def)
	{
		if (def != null)
		{
			if (!ActiveFactionEdits.TryGetValue(((Def)def).defName, out var value))
			{
				return null;
			}
			return value;
		}
		return null;
	}

	public static PawnKindDef GetReplacementForPawnKind(FactionDef faction, PawnKindDef original)
	{
		if (original == PawnKindDefOf.WildMan)
		{
			faction = Preset.SpecialWildManFaction;
		}
		factionSpecificPawnKindReplacements.TryGetValue((faction, original), out var value);
		ModCore.Debug("Found replacement for " + ((Def)original).defName + " in " + ((Def)faction).defName + ": " + (((Def)(value?)).defName ?? "<null>"));
		return value ?? original;
	}

	public void ExposeData()
	{
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Invalid comparison between Unknown and I4
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Invalid comparison between Unknown and I4
		Scribe_Values.Look<bool>(ref Active, "active", true, false);
		Scribe_Deep.Look<ThingFilter>(ref ApparelStuffFilter, "apparelStuffFilter", Array.Empty<object>());
		Scribe_Deep.Look<DefRef<FactionDef>>(ref Faction, "faction", Array.Empty<object>());
		Scribe_Values.Look<TechLevel?>(ref TechLevel, "techLevel", (TechLevel?)null, false);
		Scribe_Deep.Look<DefRef<PawnKindDef>>(ref BasicMemberKind, "basicMemberKind", Array.Empty<object>());
		Scribe_Values.Look<string>(ref ForcedPrimaryIdeoKey, "forcedPrimaryIdeoKey", (string)null, false);
		Scribe_Values.Look<ForcedIdeoSource>(ref ForcedPrimaryIdeoSourceKind, "forcedPrimaryIdeoSourceKind", ForcedIdeoSource.SavedFile, false);
		Scribe_Collections.Look<PawnKindEdit>(ref KindEdits, "kindEdits", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<string, float>(ref xenotypeChances, "xenotypeChances", (LookMode)1, (LookMode)1);
		if ((int)Scribe.mode == 1)
		{
			MaterializeXenotypeChances();
		}
		Scribe_Values.Look<bool>(ref OverrideFactionXenotypes, "overrideFactionXenotypes", false, false);
		Scribe_Collections.Look<PawnGroupMakerEdit>(ref PawnGroupMakerEdits, "groupEdits", (LookMode)2, Array.Empty<object>());
		ExposeModuleFactionData();
		if ((int)Scribe.mode == 4)
		{
			if (BasicMemberKind == null)
			{
				BasicMemberKind = new DefRef<PawnKindDef>();
			}
			if (xenotypeChances == null)
			{
				xenotypeChances = new Dictionary<string, float>();
			}
			MaterializeXenotypeChances();
			if (!GenDictionary.NullOrEmpty<string, float>(xenotypeChances) || !GenDictionary.NullOrEmpty<XenotypeDef, float>(xenotypeChancesByDef))
			{
				OverrideFactionXenotypes = true;
			}
		}
	}

	private void ExposeModuleFactionData()
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
			XmlNode xmlNode = Scribe.loader.curXmlParent?["factionModules"];
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
							module.ExposeFactionData(this);
						}
						catch (Exception e)
						{
							ModCore.Error("Error loading faction module data for '" + module.ModuleName + "' (key: " + module.ModuleKey + ")", e);
						}
						Scribe.loader.curXmlParent = curXmlParent;
					}
					else
					{
						if (preservedFactionModuleXml == null)
						{
							preservedFactionModuleXml = new Dictionary<string, string>();
						}
						preservedFactionModuleXml[childNode.Name] = childNode.InnerXml;
						ModCore.Debug("Preserving faction module data for absent module '" + childNode.Name + "'");
					}
				}
				return;
			}
		}
		if ((int)Scribe.mode == 1)
		{
			bool num = modules.Any((ITotalControlModule m) => m.IsActive);
			Dictionary<string, string> dictionary = preservedFactionModuleXml;
			bool flag = dictionary != null && dictionary.Count > 0;
			if (!num && !flag)
			{
				return;
			}
			Scribe.saver.EnterNode("factionModules");
			try
			{
				foreach (ITotalControlModule item in modules)
				{
					if (item.IsActive)
					{
						Scribe.saver.EnterNode(item.ModuleKey);
						try
						{
							item.ExposeFactionData(this);
						}
						catch (Exception e2)
						{
							ModCore.Error("Error saving faction module data for '" + item.ModuleName + "' (key: " + item.ModuleKey + ")", e2);
						}
						Scribe.saver.ExitNode();
					}
				}
				if (preservedFactionModuleXml == null)
				{
					return;
				}
				HashSet<string> hashSet = new HashSet<string>(from m in modules
					where m.IsActive
					select m.ModuleKey);
				foreach (KeyValuePair<string, string> item2 in preservedFactionModuleXml)
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
					item3.ExposeFactionData(this);
				}
				catch (Exception e3)
				{
					ModCore.Error("Error in post-load init for faction module '" + item3.ModuleName + "' (key: " + item3.ModuleKey + ")", e3);
				}
			}
		}
	}

	public void MaterializeXenotypeChances(bool replace = false)
	{
		if (replace)
		{
			xenotypeChancesByDef.Clear();
		}
		if (!ModLister.BiotechInstalled || GenDictionary.NullOrEmpty<string, float>(xenotypeChances))
		{
			return;
		}
		CollectionExtensions.Do<KeyValuePair<string, float>>((IEnumerable<KeyValuePair<string, float>>)xenotypeChances, (Action<KeyValuePair<string, float>>)delegate(KeyValuePair<string, float> pair)
		{
			XenotypeDef namedSilentFail = DefDatabase<XenotypeDef>.GetNamedSilentFail(pair.Key);
			if (namedSilentFail != null)
			{
				xenotypeChancesByDef[namedSilentFail] = pair.Value;
			}
			else
			{
				ModCore.Log("XenotypeDef '" + pair.Key + "' not found while processing edit for '" + Faction.DefName + "', skipping.");
			}
		});
	}

	public static void TweakAllPawnKinds(FactionDef def, Func<PawnKindDef, PawnKindDef> func)
	{
		if (def == null || func == null)
		{
			return;
		}
		if (def.pawnGroupMakers != null)
		{
			foreach (PawnGroupMaker pawnGroupMaker in def.pawnGroupMakers)
			{
				WorkOn(pawnGroupMaker.options);
				WorkOn(pawnGroupMaker.traders);
				WorkOn(pawnGroupMaker.carriers);
				WorkOn(pawnGroupMaker.guards);
			}
		}
		if (def.basicMemberKind != null)
		{
			def.basicMemberKind = func(def.basicMemberKind);
		}
		if (def.fixedLeaderKinds == null)
		{
			return;
		}
		for (int i = 0; i < def.fixedLeaderKinds.Count; i++)
		{
			PawnKindDef val = func(def.fixedLeaderKinds[i]);
			def.fixedLeaderKinds[i] = val;
			if (val == null)
			{
				def.fixedLeaderKinds.RemoveAt(i);
				i--;
			}
		}
		void WorkOn(IList<PawnGenOption> group)
		{
			if (group == null)
			{
				return;
			}
			foreach (PawnGenOption item in group)
			{
				PawnKindDef val2 = func(item.kind);
				if (val2 != null)
				{
					item.kind = val2;
				}
			}
		}
	}

	public static IReadOnlyList<PawnKindDef> GetAllPawnKinds(FactionDef def)
	{
		if (def == null)
		{
			return Array.Empty<PawnKindDef>();
		}
		IEnumerable<PawnGroupMaker> pawnGroupMakers = def.pawnGroupMakers;
		HashSet<PawnKindDef> hashSet = (from pgo in (pawnGroupMakers ?? Enumerable.Empty<PawnGroupMaker>()).SelectMany((PawnGroupMaker @group) => GenCollection.ConcatIfNotNull<PawnGenOption>(GenCollection.ConcatIfNotNull<PawnGenOption>(GenCollection.ConcatIfNotNull<PawnGenOption>(GenCollection.ConcatIfNotNull<PawnGenOption>(Enumerable.Empty<PawnGenOption>(), (IEnumerable<PawnGenOption>)@group.options), (IEnumerable<PawnGenOption>)@group.traders), (IEnumerable<PawnGenOption>)@group.carriers), (IEnumerable<PawnGenOption>)@group.guards))
			select pgo.kind).ToHashSet();
		if (def.basicMemberKind != null)
		{
			hashSet.Add(def.basicMemberKind);
		}
		if (def.fixedLeaderKinds != null)
		{
			GenCollection.AddRange<PawnKindDef>(hashSet, def.fixedLeaderKinds);
		}
		if (DefCache.DefaultFactionKinds != null && DefCache.DefaultFactionKinds.TryGetValue(def, out var value))
		{
			GenCollection.AddRange<PawnKindDef>(hashSet, value);
		}
		return hashSet.ToArray();
	}

	public static void ClearState()
	{
		originalFactionDefs.Clear();
		factionSpecificPawnKindReplacements.Clear();
		ActiveFactionEdits.Clear();
	}

	public static FactionDef TryGetOriginal(string factionDefName)
	{
		if (factionDefName == null)
		{
			return null;
		}
		if (!originalFactionDefs.TryGetValue(factionDefName, out var value))
		{
			return null;
		}
		return value;
	}

	private static FactionDef EnsureOriginal(FactionDef def)
	{
		if (def == null || originalFactionDefs.ContainsKey(((Def)def).defName))
		{
			return def;
		}
		FactionDef value = CloningUtility.Clone(def);
		originalFactionDefs.Add(((Def)def).defName, value);
		return def;
	}

	public List<PawnGroupMakerEdit> GetOrInitPawnGroupMakerEdits()
	{
		if (PawnGroupMakerEdits != null)
		{
			return PawnGroupMakerEdits;
		}
		FactionDef def = Faction.Def;
		if (def?.pawnGroupMakers == null)
		{
			PawnGroupMakerEdits = new List<PawnGroupMakerEdit>();
			return PawnGroupMakerEdits;
		}
		PawnGroupMakerEdits = def.pawnGroupMakers.Select(PawnGroupMakerEdit.FromPawnGroupMaker).ToList();
		return PawnGroupMakerEdits;
	}

	public void ResetGroupEdits()
	{
		PawnGroupMakerEdits = null;
	}

	public IEnumerable<PawnKindDef> GetAllKindDefsForUI()
	{
		IEnumerable<PawnKindDef> enumerable;
		if (PawnGroupMakerEdits == null)
		{
			IEnumerable<PawnKindDef> allPawnKinds = GetAllPawnKinds(Faction.Def);
			enumerable = allPawnKinds;
		}
		else
		{
			enumerable = PawnGroupMakerEdits.SelectMany((PawnGroupMakerEdit g) => g.GetAllKinds()).Distinct();
		}
		IEnumerable<PawnKindDef> enumerable2 = enumerable;
		if (EffectiveBasicMemberKind != null)
		{
			enumerable2 = enumerable2.Append(EffectiveBasicMemberKind).Distinct();
		}
		return enumerable2;
	}

	public HashSet<PawnKindDef> GetOrphanedKinds()
	{
		HashSet<string> inGroups = (from k in GetAllKindDefsForUI()
			select ((Def)PawnKindEdit.NormaliseDef(k)).defName).ToHashSet();
		return (from e in KindEdits
			where e.Def != null && !e.IsGlobal && !inGroups.Contains(((Def)e.Def).defName)
			select e.Def).ToHashSet();
	}

	public bool HasEditFor(PawnKindDef def)
	{
		return GetEditFor(def) != null;
	}

	public PawnKindEdit GetEditFor(PawnKindDef def)
	{
		if (def != null)
		{
			return KindEdits.FirstOrDefault((PawnKindEdit edit) => edit.AppliesTo(def));
		}
		return null;
	}

	public bool HasGlobalEditor()
	{
		return GetGlobalEditor() != null;
	}

	public PawnKindEdit GetGlobalEditor()
	{
		return KindEdits.FirstOrDefault((PawnKindEdit edit) => edit.IsGlobal);
	}

	public void Apply(FactionDef def, bool updateDefDatabase = true)
	{
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f3: Expected O, but got Unknown
		//IL_044c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0456: Expected O, but got Unknown
		//IL_02b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02be: Expected O, but got Unknown
		//IL_0328: Unknown result type (might be due to invalid IL or missing references)
		//IL_0332: Expected O, but got Unknown
		if (!Active)
		{
			ModCore.Warn("Applying faction edit to " + ((Def)def).label + ", but this edit is not active!");
		}
		def = EnsureOriginal(def);
		ActiveFactionEdits[((Def)def).defName] = this;
		if (PawnGroupMakerEdits != null)
		{
			def.pawnGroupMakers = PawnGroupMakerEdits.Select((PawnGroupMakerEdit e) => e.ToPawnGroupMaker()).ToList();
		}
		foreach (ITotalControlModule module in ModuleRegistry.Modules)
		{
			if (module.IsActive)
			{
				try
				{
					module.ApplyFaction(this, def);
				}
				catch (Exception e2)
				{
					ModCore.Error("Error applying faction module '" + module.ModuleName + "'", e2);
				}
			}
		}
		PawnKindEdit globalEditor = GetGlobalEditor();
		int? obj;
		if (globalEditor == null)
		{
			obj = null;
		}
		else
		{
			SimpleCurve raidCommonalityFromPointsCurve = globalEditor.RaidCommonalityFromPointsCurve;
			obj = ((raidCommonalityFromPointsCurve != null) ? new int?(raidCommonalityFromPointsCurve.PointsCount) : ((int?)null));
		}
		int? num = obj;
		if (num.GetValueOrDefault() > 0)
		{
			def.raidCommonalityFromPointsCurve = globalEditor.RaidCommonalityFromPointsCurve;
		}
		int? obj2;
		if (globalEditor == null)
		{
			obj2 = null;
		}
		else
		{
			SimpleCurve raidLootValueFromPointsCurve = globalEditor.RaidLootValueFromPointsCurve;
			obj2 = ((raidLootValueFromPointsCurve != null) ? new int?(raidLootValueFromPointsCurve.PointsCount) : ((int?)null));
		}
		num = obj2;
		if (num.GetValueOrDefault() > 0)
		{
			def.raidLootValueFromPointsCurve = globalEditor.RaidLootValueFromPointsCurve;
		}
		int? obj3;
		if (globalEditor == null)
		{
			obj3 = null;
		}
		else
		{
			SimpleCurve maxPawnCostPerTotalPointsCurve = globalEditor.MaxPawnCostPerTotalPointsCurve;
			obj3 = ((maxPawnCostPerTotalPointsCurve != null) ? new int?(maxPawnCostPerTotalPointsCurve.PointsCount) : ((int?)null));
		}
		num = obj3;
		if (num.GetValueOrDefault() > 0)
		{
			def.maxPawnCostPerTotalPointsCurve = globalEditor.MaxPawnCostPerTotalPointsCurve;
		}
		if (TechLevel.HasValue)
		{
			def.techLevel = TechLevel.Value;
		}
		DefRef<PawnKindDef> basicMemberKind = BasicMemberKind;
		if (basicMemberKind != null && basicMemberKind.HasValue)
		{
			def.basicMemberKind = BasicMemberKind.Def;
		}
		foreach (PawnKindDef allPawnKind in GetAllPawnKinds(def))
		{
			PawnKindDef val = PawnKindEdit.NormaliseDef(allPawnKind);
			PawnKindEdit editFor = GetEditFor(val);
			PawnKindDef val2 = ((globalEditor != null || editFor != null) ? CloningUtility.Clone(val) : val);
			globalEditor?.Apply(val2, null);
			PawnKindDef val3 = editFor?.Apply(val2, globalEditor);
			if (val3 != null && val3 != val2)
			{
				val2 = val3;
			}
			if (ModsConfig.BiotechActive && (xenotypeChancesByDef?.Count ?? 0) >= 1 && editFor != null && !editFor.ForceSpecificXenos && val2.RaceProps.Humanlike)
			{
				PawnKindDef val4 = val2;
				if (val4.xenotypeSet == null)
				{
					val4.xenotypeSet = new XenotypeSet();
				}
				XenotypeSet xenotypeSet = val2.xenotypeSet;
				if (xenotypeSet.xenotypeChances == null)
				{
					xenotypeSet.xenotypeChances = new List<XenotypeChance>();
				}
				val2.xenotypeSet.xenotypeChances.Clear();
				foreach (KeyValuePair<XenotypeDef, float> item in xenotypeChancesByDef ?? new Dictionary<XenotypeDef, float>())
				{
					val2.xenotypeSet.xenotypeChances.Add(new XenotypeChance(item.Key, item.Value));
				}
			}
			if ((globalEditor != null && globalEditor.RenameDef) || (editFor != null && editFor.RenameDef))
			{
				List<PawnKindEdit> list = PawnKindEdit.RemoveActiveEdits(val2);
				((Def)val2).defName = GetNewNameForPawnKind(val, def);
				if (list != null)
				{
					PawnKindEdit.SetActiveEdits(val2, list);
				}
				PawnKindEdit.RecordReplacement(val, val2);
				if (updateDefDatabase)
				{
					DefDatabase<PawnKindDef>.Add(val2);
				}
			}
			if (val != val2)
			{
				ReplaceKind(def, val, val2);
			}
		}
		if (!ModsConfig.BiotechActive || GenDictionary.NullOrEmpty<XenotypeDef, float>(xenotypeChancesByDef))
		{
			return;
		}
		FactionDef val5 = def;
		if (val5.xenotypeSet == null)
		{
			val5.xenotypeSet = new XenotypeSet();
		}
		def.xenotypeSet?.xenotypeChances?.Clear();
		foreach (KeyValuePair<XenotypeDef, float> item2 in xenotypeChancesByDef)
		{
			def.xenotypeSet?.xenotypeChances?.Add(new XenotypeChance(item2.Key, item2.Value));
		}
	}

	public static string GetNewNameForPawnKind(PawnKindDef pawnKindDef, FactionDef factionDef)
	{
		return ((Def)pawnKindDef).defName + "_TCCln_" + ((Def)factionDef).defName;
	}

	private void ReplaceKind(FactionDef faction, PawnKindDef original, PawnKindDef replacement)
	{
		ModCore.Debug("Replacing PawnKind '" + (((Def)(original?)).defName ?? "<null>") + "' with '" + (((Def)(replacement?)).defName ?? "<null>") + "' in faction " + ((Def)faction).defName);
		TweakAllPawnKinds(faction, (PawnKindDef current) => (current != original) ? current : replacement);
		GenCollection.SetOrAdd<(FactionDef, PawnKindDef), PawnKindDef>(factionSpecificPawnKindReplacements, (faction, original), replacement);
	}

	public void CopyFrom(FactionEdit source)
	{
		TechLevel = source.TechLevel;
		BasicMemberKind = source.BasicMemberKind?.DeepClone() ?? new DefRef<PawnKindDef>();
		ForcedPrimaryIdeoKey = source.ForcedPrimaryIdeoKey;
		ForcedPrimaryIdeoSourceKind = source.ForcedPrimaryIdeoSourceKind;
		OverrideFactionXenotypes = source.OverrideFactionXenotypes;
		xenotypeChances = ((source.xenotypeChances != null) ? new Dictionary<string, float>(source.xenotypeChances) : new Dictionary<string, float>());
		xenotypeChancesByDef = ((source.xenotypeChancesByDef != null) ? new Dictionary<XenotypeDef, float>(source.xenotypeChancesByDef) : new Dictionary<XenotypeDef, float>());
	}

	public override string ToString()
	{
		return $"FactionEdit [{Faction}]";
	}
}
