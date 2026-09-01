using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using FactionLoadout.Modules;
using FactionLoadout.Patches;
using FactionLoadout.UISupport;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class ModCore : Mod
{
	public Dialog_FactionLoadout settingsDialog;

	public static MySettings Settings;

	public Dialog_FactionLoadout SettingsDialog => settingsDialog ?? (settingsDialog = new Dialog_FactionLoadout());

	public static void Debug(string msg)
	{
		if (MySettings.VerboseLogging)
		{
			Log.Message("<color=#1c6beb>[FacLoadout] [DEBUG]</color> " + (msg ?? "<null>"));
		}
	}

	public static void Log(string msg)
	{
		Log.Message("<color=#1c6beb>[FacLoadout]</color> " + (msg ?? "<null>"));
	}

	public static void Warn(string msg)
	{
		Log.Warning("<color=#1c6beb>[FacLoadout]</color> " + (msg ?? "<null>"));
	}

	public static void Error(string msg, Exception e = null)
	{
		Log.Error("<color=#1c6beb>[FacLoadout]</color> " + (msg ?? "<null>"));
		if (e != null)
		{
			Log.Error(e.ToString());
		}
	}

	public ModCore(ModContentPack content)
		: base(content)
	{
		Settings = ((Mod)this).GetSettings<MySettings>();
		LongEventHandler.QueueLongEvent((Action)LoadLate, "FactionLoadout_LoadingScreenText", false, (Action<Exception>)null, true, false, (Action)null);
	}

	public override string SettingsCategory()
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(Translator.Translate("FactionLoadout_SettingName"));
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		((Window)SettingsDialog).DoWindowContents(inRect);
	}

	private void LoadLate()
	{
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_008a: Expected O, but got Unknown
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Expected O, but got Unknown
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Expected O, but got Unknown
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Expected O, but got Unknown
		//IL_0184: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Expected O, but got Unknown
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dd: Expected O, but got Unknown
		//IL_021c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Expected O, but got Unknown
		//IL_0258: Unknown result type (might be due to invalid IL or missing references)
		//IL_025f: Expected O, but got Unknown
		//IL_02ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b8: Expected O, but got Unknown
		//IL_02e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f3: Expected O, but got Unknown
		//IL_039e: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ab: Expected O, but got Unknown
		//IL_03da: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e6: Expected O, but got Unknown
		//IL_040e: Unknown result type (might be due to invalid IL or missing references)
		//IL_041b: Expected O, but got Unknown
		//IL_0443: Unknown result type (might be due to invalid IL or missing references)
		//IL_0450: Expected O, but got Unknown
		//IL_0328: Unknown result type (might be due to invalid IL or missing references)
		//IL_0335: Expected O, but got Unknown
		//IL_0364: Unknown result type (might be due to invalid IL or missing references)
		//IL_0370: Expected O, but got Unknown
		//IL_04b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c5: Expected O, but got Unknown
		//IL_0484: Unknown result type (might be due to invalid IL or missing references)
		//IL_0490: Expected O, but got Unknown
		ModuleRegistry.InitializeAll();
		Preset.LoadAllPresets();
		int num = 0;
		int num2 = 0;
		foreach (Preset loadedPreset in Preset.LoadedPresets)
		{
			if (!(MySettings.ActivePreset != loadedPreset.GUID))
			{
				int num3 = loadedPreset.TryApplyAll();
				num2 += num3;
				num++;
				Messages.Message($"Applied faction edit '{loadedPreset.Name}': modified {num3} factions.", MessageTypeDefOf.PositiveEvent, true);
			}
		}
		Harmony val = new Harmony("co.uk.epicguru.factionloadout");
		val.Patch((MethodBase)AccessTools.Method(typeof(PawnApparelGenerator), "GenerateStartingApparelFor", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(ApparelGenPatch), "Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(PawnApparelGenerator), "CanUsePair", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(CanUsePairBlacklistPatch), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(Faction), "TryGenerateNewLeader", (Type[])null, (Type[])null), new HarmonyMethod(AccessTools.Method(typeof(FactionLeaderPatch), "Prefix", (Type[])null, (Type[])null), 800, (string[])null, (string[])null, (bool?)null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(FactionUtility), "HostileTo", (Type[])null, (Type[])null), new HarmonyMethod(AccessTools.Method(typeof(FactionUtilityPawnGenPatch), "Prefix", (Type[])null, (Type[])null), 800, (string[])null, (string[])null, (bool?)null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(ThingIDMaker), "GiveIDTo", (Type[])null, (Type[])null), new HarmonyMethod(AccessTools.Method(typeof(ThingIDPatch), "Prefix", (Type[])null, (Type[])null), 800, (string[])null, (string[])null, (bool?)null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(IdeoUtility), "IdeoChangeToWeight", (Type[])null, (Type[])null), new HarmonyMethod(AccessTools.Method(typeof(IdeoUtilityPatch), "Prefix", (Type[])null, (Type[])null), 800, (string[])null, (string[])null, (bool?)null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		MethodInfo methodInfo = AccessTools.Method(typeof(PawnWeaponGenerator), "TryGenerateWeaponFor", (Type[])null, (Type[])null);
		HarmonyMethod val2 = new HarmonyMethod(AccessTools.Method(typeof(WeaponGenPatch), "Postfix", (Type[])null, (Type[])null));
		val2.before = new string[1] { "CombatExtended.HarmonyCE" };
		val.Patch((MethodBase)methodInfo, (HarmonyMethod)null, val2, (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(PawnWeaponGenerator), "GetCommonality", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(WeaponGetCommonalityBlacklistPatch), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(PawnGenerator), "GenerateNewPawnInternal", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(PawnGenPatchCore), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		if (ModsConfig.IdeologyActive)
		{
			val.Patch((MethodBase)AccessTools.Method(typeof(PawnGenerator), "GenerateNewPawnInternal", (Type[])null, (Type[])null), new HarmonyMethod(AccessTools.Method(typeof(PawnGenPatchIdeo), "Prefix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
			val.Patch((MethodBase)AccessTools.Method(typeof(FactionManager), "Add", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(FactionAddIdeoPatch), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		}
		val.Patch((MethodBase)AccessTools.Method(typeof(PawnGenerator), "GenerateRandomAge", (Type[])null, (Type[])null), new HarmonyMethod(AccessTools.Method(typeof(PawnGenAgePatchCore), "Prefix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(PawnGenerator), "GetBodyTypeFor", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(PawnGenPatchBodyTypeDef), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(OptionListingUtility), "DrawOptionListing", (Type[])null, (Type[])null), new HarmonyMethod(typeof(OptionListingUtility_Patch), "DrawOptionListing_Patch", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		val.Patch((MethodBase)AccessTools.Method(typeof(Pawn_GuestTracker), "SetupRecruitable", (Type[])null, (Type[])null), new HarmonyMethod(typeof(PawnGenPatchRecruitable), "Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		if (MySettings.PatchKindInRequests)
		{
			val.Patch((MethodBase)AccessTools.PropertyGetter(typeof(PawnGenerationRequest), "KindDef"), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(PawnGenRequestKindPatch), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		}
		val.Patch((MethodBase)AccessTools.Method(typeof(PlayDataLoader), "HotReloadDefs", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HotReloadDefsHook), "Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		Preset.AddMissingSpecialFactionsIfNeeded();
		RewarmVEFactionCache();
		ForcedIdeoGameComponent.RecomputeAnyEditsActive();
		Log($"Game comp finalized init, applied {num} presets that affected {num2} factions.");
	}

	private static void RemoveTCClonesFromDefDatabase()
	{
		List<PawnKindDef> list = DefDatabase<PawnKindDef>.AllDefsListForReading.Where((PawnKindDef d) => ((Def)d).defName.Contains("_TCCln_")).ToList();
		foreach (PawnKindDef item in list)
		{
			DefDatabase<PawnKindDef>.defsList.Remove(item);
			DefDatabase<PawnKindDef>.defsByName.Remove(((Def)item).defName);
			DefDatabase<PawnKindDef>.defsByShortHash.Remove(((Def)item).shortHash);
		}
		Debug($"Removed {list.Count} TC clone defs from DefDatabase before reapply.");
	}

	public static void ReapplyAfterHotReload()
	{
		Log("Hot reload detected - reapplying Total Control preset...");
		RemoveTCClonesFromDefDatabase();
		FactionEdit.ClearState();
		PawnKindEdit.ClearState();
		int num = 0;
		int num2 = 0;
		foreach (Preset loadedPreset in Preset.LoadedPresets)
		{
			if (!(MySettings.ActivePreset != loadedPreset.GUID))
			{
				int num3 = loadedPreset.TryApplyAll();
				num2 += num3;
				num++;
			}
		}
		Preset.AddMissingSpecialFactionsIfNeeded();
		RewarmVEFactionCache();
		ForcedIdeoGameComponent.RecomputeAnyEditsActive();
		Log($"Reapply after hot reload complete: applied {num} presets affecting {num2} factions.");
	}

	public static void RewarmVEFactionCache()
	{
		AccessTools.Method(AccessTools.TypeByName("VFECore.ScenPartUtility"), "SetCache", (Type[])null, (Type[])null)?.Invoke(null, null);
	}
}
