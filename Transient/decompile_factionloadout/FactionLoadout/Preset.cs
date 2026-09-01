using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FactionLoadout.Util;
using RimWorld;
using Verse;

namespace FactionLoadout;

public class Preset : IExposable
{
	private static List<Preset> loadedPresets = new List<Preset>();

	public static string SpecialCreepjoinerFactionDefName = "FactionLoadout_Special_CreepJoiner";

	public static string SpecialWildManFactionDefName = "FactionLoadout_Special_WildMan";

	public static string SpecialFactionlessPawnsFactionDefName = "FactionLoadout_Special_Factionless";

	public static FactionDef SpecialCreepjoinerFaction = new FactionDef
	{
		hidden = true,
		defName = SpecialCreepjoinerFactionDefName,
		label = "Special CreepJoiner",
		description = "This is a special faction that is used to edit a faux CreepJoiner faction.",
		humanlikeFaction = true,
		raidsForbidden = true,
		requiredCountAtGameStart = 0,
		pawnGroupMakers = new List<PawnGroupMaker>(1)
		{
			new PawnGroupMaker
			{
				kindDef = PawnGroupKindDefOf.Combat,
				options = ((IEnumerable<CreepJoinerFormKindDef>)DefDatabase<CreepJoinerFormKindDef>.AllDefsListForReading).Select((Func<CreepJoinerFormKindDef, PawnGenOption>)((CreepJoinerFormKindDef creepKind) => new PawnGenOption
				{
					kind = (PawnKindDef)(object)creepKind
				})).ToList()
			}
		}
	};

	public static FactionDef SpecialWildManFaction = new FactionDef
	{
		hidden = true,
		defName = SpecialWildManFactionDefName,
		label = "Special WildMan",
		description = "This is a special faction that is used to edit a faux WildMan faction.",
		humanlikeFaction = true,
		raidsForbidden = true,
		requiredCountAtGameStart = 0,
		basicMemberKind = PawnKindDefOf.WildMan
	};

	public static FactionDef SpecialFactionlessPawnsFaction = new FactionDef
	{
		hidden = true,
		defName = SpecialFactionlessPawnsFactionDefName,
		label = "Factionless Pawns",
		description = "A special group for editing humanlike pawnkinds that don't belong to any faction. Populated automatically at startup.",
		humanlikeFaction = true,
		raidsForbidden = true,
		requiredCountAtGameStart = 0
	};

	public static HashSet<PawnKindDef> FactionlessPawnKindsSet = new HashSet<PawnKindDef>();

	public string Name = "My preset";

	public List<FactionEdit> factionChanges = new List<FactionEdit>();

	public bool IsPackaged;

	public string PackagedFilePath;

	public TCPresetPackageDef SourcePackageDef;

	private string guid;

	public static IReadOnlyList<Preset> LoadedPresets => loadedPresets;

	public string PackagedModName
	{
		get
		{
			TCPresetPackageDef sourcePackageDef = SourcePackageDef;
			object obj;
			if (sourcePackageDef == null)
			{
				obj = null;
			}
			else
			{
				ModContentPack modContentPack = ((Def)sourcePackageDef).modContentPack;
				obj = ((modContentPack != null) ? modContentPack.Name : null);
			}
			if (obj == null)
			{
				obj = "Unknown mod";
			}
			return (string)obj;
		}
	}

	public string GUID
	{
		get
		{
			if (guid == null)
			{
				EnsureGUID();
			}
			return guid;
		}
	}

	public static void LoadAllPresets()
	{
		loadedPresets.Clear();
		foreach (FileInfo item2 in IO.ListXmlFiles(IO.SaveDataPath))
		{
			try
			{
				Preset item = new Preset();
				IO.LoadFromFile((IExposable)(object)item, item2.FullName);
				loadedPresets.Add(item);
			}
			catch (Exception e)
			{
				ModCore.Error("Failed to load preset from '" + item2.FullName + "'", e);
			}
		}
		foreach (TCPresetPackageDef allDef in DefDatabase<TCPresetPackageDef>.AllDefs)
		{
			if (((Def)allDef).modContentPack == null)
			{
				ModCore.Warn("TCPresetPackageDef '" + ((Def)allDef).defName + "' has no modContentPack - skipping.");
				continue;
			}
			string text = Path.Combine(((Def)allDef).modContentPack.RootDir, allDef.presetPath);
			if (!File.Exists(text))
			{
				ModCore.Warn("Packaged preset file not found: '" + text + "' (from def '" + ((Def)allDef).defName + "').");
				continue;
			}
			try
			{
				Preset preset = new Preset();
				IO.LoadFromFile((IExposable)(object)preset, text);
				if (GenCollection.Any<Preset>(loadedPresets, (Predicate<Preset>)((Preset p) => p.GUID == preset.GUID)))
				{
					ModCore.Warn("Packaged preset '" + preset.Name + "' (GUID " + preset.GUID + ") from '" + ((Def)allDef).defName + "' has a conflicting GUID with another loaded preset.");
				}
				preset.IsPackaged = true;
				preset.PackagedFilePath = text;
				preset.SourcePackageDef = allDef;
				loadedPresets.Add(preset);
			}
			catch (Exception e2)
			{
				ModCore.Error("Failed to load packaged preset from '" + text + "' (def '" + ((Def)allDef).defName + "').", e2);
			}
		}
	}

	public static void AddNewPreset(Preset preset)
	{
		if (preset != null && !loadedPresets.Contains(preset))
		{
			loadedPresets.Add(preset);
		}
	}

	public static void DeletePreset(Preset preset)
	{
		if (preset == null || !loadedPresets.Contains(preset))
		{
			return;
		}
		loadedPresets.Remove(preset);
		if (preset.IsPackaged)
		{
			return;
		}
		try
		{
			preset.DeleteFile();
		}
		catch (Exception e)
		{
			ModCore.Error("Failed to delete preset file for " + preset.Name + " (" + preset.GUID + ")", e);
		}
	}

	public static Preset CreateCopy(Preset source)
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		string text = Path.Combine(Path.GetTempPath(), $"TC_preset_copy_{Guid.NewGuid()}.xml");
		try
		{
			IO.SaveToFile((IExposable)(object)source, text);
			Preset preset = new Preset();
			IO.LoadFromFile((IExposable)(object)preset, text);
			preset.guid = null;
			preset.IsPackaged = false;
			preset.PackagedFilePath = null;
			preset.SourcePackageDef = null;
			string name = source.Name;
			TaggedString val = Translator.Translate("FactionLoadout_CopySuffix");
			preset.Name = name + " " + ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
			return preset;
		}
		finally
		{
			if (File.Exists(text))
			{
				File.Delete(text);
			}
		}
	}

	public void ExposeData()
	{
		EnsureGUID();
		Scribe_Values.Look<string>(ref Name, "name", "My preset", false);
		Scribe_Values.Look<string>(ref guid, "guid", (string)null, false);
		AddMissingSpecialFactionsIfNeeded();
		Scribe_Collections.Look<FactionEdit>(ref factionChanges, "factionChanges", (LookMode)2, Array.Empty<object>());
	}

	public static void AddMissingSpecialFactionsIfNeeded()
	{
		if (DefDatabase<FactionDef>.GetNamed(SpecialCreepjoinerFactionDefName, false) == null)
		{
			DefDatabase<FactionDef>.Add(SpecialCreepjoinerFaction);
		}
		if (DefDatabase<FactionDef>.GetNamed(SpecialWildManFactionDefName, false) == null)
		{
			DefDatabase<FactionDef>.Add(SpecialWildManFaction);
		}
		if (DefDatabase<FactionDef>.GetNamed(SpecialFactionlessPawnsFactionDefName, false) == null)
		{
			DefDatabase<FactionDef>.Add(SpecialFactionlessPawnsFaction);
		}
		PopulateFactionlessPawnKinds();
	}

	public static void PopulateFactionlessPawnKinds()
	{
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_0234: Unknown result type (might be due to invalid IL or missing references)
		//IL_0240: Expected O, but got Unknown
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Expected O, but got Unknown
		HashSet<PawnKindDef> inAnyFaction = new HashSet<PawnKindDef>();
		foreach (FactionDef item in DefDatabase<FactionDef>.AllDefsListForReading)
		{
			if (((Def)item).defName == SpecialCreepjoinerFactionDefName || ((Def)item).defName == SpecialWildManFactionDefName || ((Def)item).defName == SpecialFactionlessPawnsFactionDefName)
			{
				continue;
			}
			if (item.pawnGroupMakers != null)
			{
				foreach (PawnGroupMaker pawnGroupMaker in item.pawnGroupMakers)
				{
					AddOptions(pawnGroupMaker.options);
					AddOptions(pawnGroupMaker.guards);
					AddOptions(pawnGroupMaker.traders);
					AddOptions(pawnGroupMaker.carriers);
				}
			}
			if (item.basicMemberKind != null)
			{
				inAnyFaction.Add(item.basicMemberKind);
			}
			if (item.fixedLeaderKinds == null)
			{
				continue;
			}
			foreach (PawnKindDef fixedLeaderKind in item.fixedLeaderKinds)
			{
				inAnyFaction.Add(fixedLeaderKind);
			}
		}
		FactionlessPawnKindsSet.Clear();
		List<PawnGenOption> list2 = new List<PawnGenOption>();
		foreach (PawnKindDef item2 in DefDatabase<PawnKindDef>.AllDefsListForReading)
		{
			ThingDef race = item2.race;
			if (race != null)
			{
				RaceProperties race2 = race.race;
				if (((race2 != null) ? new bool?(race2.Humanlike) : ((bool?)null)) == true && item2 != PawnKindDefOf.WildMan && !(item2 is CreepJoinerFormKindDef) && !inAnyFaction.Contains(item2))
				{
					FactionlessPawnKindsSet.Add(item2);
					list2.Add(new PawnGenOption
					{
						kind = item2
					});
				}
			}
		}
		SpecialFactionlessPawnsFaction.pawnGroupMakers = ((list2.Count > 0) ? new List<PawnGroupMaker>(1)
		{
			new PawnGroupMaker
			{
				kindDef = PawnGroupKindDefOf.Combat,
				options = list2
			}
		} : null);
		void AddOptions(List<PawnGenOption> list)
		{
			if (list == null)
			{
				return;
			}
			foreach (PawnGenOption item3 in list)
			{
				if (item3.kind != null)
				{
					inAnyFaction.Add(item3.kind);
				}
			}
		}
	}

	public static void SetupRelationsForFaction(Faction faction)
	{
		foreach (Faction item in Find.FactionManager.AllFactionsListForReading)
		{
			if (faction != item)
			{
				faction.TryMakeInitialRelationsWith(item);
			}
		}
	}

	public bool HasMissingFactions()
	{
		foreach (FactionEdit factionChange in factionChanges)
		{
			if (factionChange.Faction.IsMissing)
			{
				return true;
			}
		}
		return false;
	}

	public bool HasEditFor(FactionDef def)
	{
		if (def == null)
		{
			return false;
		}
		foreach (FactionEdit factionChange in factionChanges)
		{
			if (factionChange.Faction.HasValue && factionChange.Faction.Def == def)
			{
				return true;
			}
		}
		return false;
	}

	public IEnumerable<string> GetMissingFactionAndModNames()
	{
		foreach (FactionEdit factionChange in factionChanges)
		{
			if (factionChange.Faction.IsMissing)
			{
				yield return "'" + factionChange.Faction.DefName + "' from mod: <b>" + factionChange.Faction.ModName + "</b>";
			}
		}
	}

	public int TryApplyAll()
	{
		int num = 0;
		foreach (FactionEdit factionChange in factionChanges)
		{
			if (factionChange.Active)
			{
				if (factionChange.Faction.IsMissing)
				{
					ModCore.Warn("Faction '" + factionChange.Faction.DefName + "' is not loaded, so changes will not be applied.");
				}
				else if (factionChange.Faction.HasValue)
				{
					factionChange.Apply(factionChange.Faction.Def);
					num++;
					ModCore.Log("  - Applied changes to " + factionChange.Faction.LabelCap);
				}
			}
		}
		ModCore.Log($"Applied preset '{Name}': {num} factions were edited.");
		return num;
	}

	private void EnsureGUID()
	{
		if (guid == null)
		{
			guid = "";
			Random random = new Random();
			char[] array = new char[10] { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' };
			for (int i = 0; i < 16; i++)
			{
				guid += array[random.Next(array.Length)];
			}
		}
	}

	public void Save()
	{
		if (IsPackaged && PackagedFilePath != null)
		{
			IO.SaveToFile((IExposable)(object)this, PackagedFilePath);
			return;
		}
		EnsureGUID();
		string path = guid + ".xml";
		string filePath = Path.Combine(IO.SaveDataPath, path);
		IO.SaveToFile((IExposable)(object)this, filePath);
	}

	public bool DeleteFile()
	{
		string path = guid + ".xml";
		return IO.DeleteFile(Path.Combine(IO.SaveDataPath, path));
	}
}
