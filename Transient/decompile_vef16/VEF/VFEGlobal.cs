using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using VEF.Factions;
using VEF.Weathers;
using Verse;

namespace VEF;

public class VFEGlobal : Mod
{
	public static VFEGlobalSettings settings;

	private Vector2 scrollPosition = Vector2.zero;

	protected readonly Vector2 ButtonSize = new Vector2(120f, 40f);

	private int PageIndex;

	private int FactionCanBeAddedCount;

	private int ToggablePatchCount;

	private int ModUsingToggablePatchCount;

	private bool initialized;

	public VFEGlobal(ModContentPack content)
		: base(content)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		settings = ((Mod)this).GetSettings<VFEGlobalSettings>();
		BackwardsCompatibilityFixer.FixSettingsNameOrNamespace((Mod)(object)this, (ModSettings)(object)settings);
		GenRadialPatches.IncreaseRadialPatternRadiiSize();
	}

	public override string SettingsCategory()
	{
		return "Vanilla Expanded Framework";
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Expected O, but got Unknown
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Expected O, but got Unknown
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Expected O, but got Unknown
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(inRect);
		((Rect)(ref val)).y = ((Rect)(ref inRect)).y + 40f;
		Rect val2 = val;
		((Rect)(ref val))._002Ector(inRect);
		((Rect)(ref val)).height = ((Rect)(ref inRect)).height - 40f;
		((Rect)(ref val)).y = ((Rect)(ref inRect)).y + 40f;
		Rect val3 = val;
		Widgets.DrawMenuSection(val3);
		List<TabRecord> list = new List<TabRecord>
		{
			new TabRecord(TaggedString.op_Implicit(Translator.Translate("VEF_GeneralTitle")), (Action)delegate
			{
				PageIndex = 0;
				((Mod)this).WriteSettings();
			}, PageIndex == 0),
			new TabRecord(TaggedString.op_Implicit(Translator.Translate("VEF_TPTitle")), (Action)delegate
			{
				PageIndex = 1;
				((Mod)this).WriteSettings();
			}, PageIndex == 1),
			new TabRecord(TaggedString.op_Implicit(Translator.Translate("VEF.WeatherDamages")), (Action)delegate
			{
				PageIndex = 2;
				((Mod)this).WriteSettings();
			}, PageIndex == 2)
		};
		TabDrawer.DrawTabs<TabRecord>(val2, list, 200f);
		switch (PageIndex)
		{
		case 0:
			GeneralSettings(GenUI.ContractedBy(val3, 15f));
			break;
		case 1:
			ToggablePatchesSettings(GenUI.ContractedBy(val3, 15f));
			break;
		case 2:
			WeatherDamageSettings(GenUI.ContractedBy(val3, 15f));
			break;
		}
	}

	private void GeneralSettings(Rect rect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Unknown result type (might be due to invalid IL or missing references)
		//IL_028b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(rect);
		Text.Font = (GameFont)1;
		val.Label(Translator.Translate("VEF_FactionDiscovery"), -1f, (string)null);
		if (Current.Game != null)
		{
			FactionCanBeAddedCount = DefDatabase<FactionDef>.AllDefs.Where(ValidatorAnyFactionLeft).Count();
			val.Label(TranslatorFormattedStringExtensions.Translate("CanAddXFaction", NamedArgument.op_Implicit(FactionCanBeAddedCount)), -1f, (string)null);
			if (FactionCanBeAddedCount > 0 && val.ButtonText(TaggedString.op_Implicit(Translator.Translate("AskForPopUp")), TaggedString.op_Implicit(Translator.Translate("AskForPopUpExplained")), 1f))
			{
				Current.Game.World.GetComponent<NewFactionSpawningState>().ClearIgnored();
				List<FactionDef> list = new List<FactionDef>();
				VanillaExpandedFramework_GameComponentUtility_LoadedGame_Patch.LoadedGame.CollectPotentialFactionsToSpawn(DefDatabase<FactionDef>.AllDefs, list);
				List<FactionDef>.Enumerator enumerator = list.GetEnumerator();
				if (enumerator.MoveNext())
				{
					Dialog_NewFactionSpawning.OpenDialog(enumerator);
				}
				else
				{
					enumerator.Dispose();
				}
			}
		}
		else
		{
			Text.Anchor = (TextAnchor)4;
			val.Label(Translator.Translate("NeedToBeInGame"), -1f, (string)null);
			Text.Anchor = (TextAnchor)0;
		}
		((Listing)val).GapLine(12f);
		((Listing)val).Gap(12f);
		val.Label(Translator.Translate("VEF_CustomStructureGeneration"), -1f, (string)null);
		((Listing)val).Gap(5f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VEF_VerboseLogging")), ref settings.enableVerboseLogging, (string)null, 0f, 1f);
		((Listing)val).GapLine(12f);
		((Listing)val).Gap(12f);
		val.Label(Translator.Translate("VEF_TextureVariations"), -1f, (string)null);
		((Listing)val).Gap(5f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VFE_RandomBuildingsDontStartRandom")), ref settings.randomStartsAsRandom, (string)null, 0f, 1f);
		((Listing)val).Gap(5f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VFE_HideRandomizeButton")), ref settings.hideRandomizeButtons, (string)null, 0f, 1f);
		((Listing)val).GapLine(12f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VEF_DisableTextureCaching")), ref settings.disableCaching, "Warning: Enabling this might cause performance issues.", 0f, 1f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VEF.DisableModSourceReport")), ref settings.disableModSourceReport, (string)null, 0f, 1f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VEF_EnablePipeSystemNoStorageAlert")), ref settings.enablePipeSystemNoStorageAlert, (string)null, 0f, 1f);
		((Listing)val).End();
	}

	private bool ValidatorAnyFactionLeft(FactionDef faction)
	{
		if (faction == null)
		{
			return false;
		}
		if (faction.isPlayer)
		{
			return false;
		}
		if (faction.hidden && faction.requiredCountAtGameStart <= 0)
		{
			return false;
		}
		if (Find.FactionManager.AllFactions.Count((Faction f) => f.def == faction) > 0)
		{
			return false;
		}
		if (NewFactionSpawningUtility.NeverSpawn(faction))
		{
			return false;
		}
		return true;
	}

	private void ToggablePatchesSettings(Rect rect)
	{
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Expected O, but got Unknown
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		if (!initialized)
		{
			initialized = true;
			foreach (ModContentPack runningMod in LoadedModManager.RunningMods)
			{
				try
				{
					if (runningMod.Patches != null)
					{
						int count = runningMod.Patches.ToList().FindAll((PatchOperation p) => p is PatchOperationToggableSequence patchOperationToggableSequence && patchOperationToggableSequence.ModsFound()).Count;
						if (count > 0)
						{
							ModUsingToggablePatchCount++;
							ToggablePatchCount += count;
						}
					}
				}
				catch (Exception ex)
				{
					Log.Error(runningMod.Name + " produced an error with XML patches: " + ex.ToString());
				}
			}
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(rect);
		((Rect)(ref val)).height = 110f + (float)(ToggablePatchCount + ModUsingToggablePatchCount) * 32f;
		((Rect)(ref val)).width = ((Rect)(ref rect)).width - 20f;
		Rect val2 = val;
		Listing_Standard val3 = new Listing_Standard();
		Widgets.BeginScrollView(rect, ref scrollPosition, val2, true);
		((Listing)val3).Begin(val2);
		Text.Anchor = (TextAnchor)4;
		val3.Label(Translator.Translate("NeedRestart"), -1f, (string)null);
		Text.Anchor = (TextAnchor)0;
		((Listing)val3).Gap(12f);
		foreach (ModContentPack item in LoadedModManager.RunningMods.OrderBy((ModContentPack m) => m.OverwritePriority).ThenBy((ModContentPack x) => LoadedModManager.RunningModsListForReading.IndexOf(x)))
		{
			if (((item != null) ? item.Patches : null) != null && item.Patches.Any((PatchOperation p) => p is PatchOperationToggableSequence patchOperationToggableSequence2 && patchOperationToggableSequence2.ModsFound()))
			{
				Text.Anchor = (TextAnchor)4;
				val3.Label(item.Name, -1f, (TipSignal?)null);
				Text.Anchor = (TextAnchor)0;
				AddButtons(val3, item);
			}
		}
		((Listing)val3).End();
		Widgets.EndScrollView();
	}

	private void AddButtons(Listing_Standard list, ModContentPack modContentPack)
	{
		foreach (PatchOperation patch in modContentPack.Patches)
		{
			if (!(patch is PatchOperationToggableSequence patchOperationToggableSequence) || !patchOperationToggableSequence.ModsFound())
			{
				continue;
			}
			string key = patchOperationToggableSequence.label.Replace(" ", "");
			string text = ((!GenDictionary.NullOrEmpty<string, bool>(settings.toggablePatch) && settings.toggablePatch.ContainsKey(key)) ? settings.toggablePatch[key].ToString() : patchOperationToggableSequence.enabled.ToString());
			if (!list.ButtonTextLabeled(patchOperationToggableSequence.label, text, (TextAnchor)0, (string)null, (string)null))
			{
				continue;
			}
			if (!GenDictionary.NullOrEmpty<string, bool>(settings.toggablePatch) && settings.toggablePatch.ContainsKey(key))
			{
				settings.toggablePatch.Remove(key);
				continue;
			}
			if (GenDictionary.NullOrEmpty<string, bool>(settings.toggablePatch))
			{
				settings.toggablePatch = new Dictionary<string, bool>();
			}
			settings.toggablePatch.Add(key, !patchOperationToggableSequence.enabled);
		}
	}

	private void WeatherDamageSettings(Rect rect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(rect);
		Text.Font = (GameFont)1;
		foreach (string item in settings.weatherDamagesOptions.Keys.ToList())
		{
			WeatherDef namedSilentFail = DefDatabase<WeatherDef>.GetNamedSilentFail(item);
			if (namedSilentFail != null && ((Def)namedSilentFail).GetModExtension<WeatherEffectsExtension>() != null)
			{
				bool value = settings.weatherDamagesOptions[item];
				val.CheckboxLabeled(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.EnableWeatherDamage", NamedArgument.op_Implicit(((Def)namedSilentFail).LabelCap))), ref value, (string)null, 0f, 1f);
				settings.weatherDamagesOptions[item] = value;
				((Listing)val).Gap(5f);
			}
		}
		((Listing)val).End();
	}
}
