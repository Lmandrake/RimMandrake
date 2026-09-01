using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class BigSmallMod : Mod
{
	public static BSSettings settings = null;

	private static Vector2 scrollPosition = Vector2.zero;

	private int selectedTab;

	private static readonly string[] tabKeys = new string[7] { "BS_General", "BS_Races", "BS_Size", "BS_AutoCombat", "BS_Extras", "BS_Advanced", "BS_Developer" };

	private static float columnWidth = 100f;

	private const float scrollAreaWidthMod = 20f;

	private string inflitratorChanceStr;

	private string inflitratorRaidChanceStr;

	private string immortalReturnFactorStr;

	private string soulPowerFalloffOffsetStr;

	private string soulPowerGainMultiplierStr;

	private string metabolismLimitOffsetStr;

	private string sapientMechsMinAgeStr;

	private string dmgExpontentStr;

	private string flatDmtStr;

	private string hungerMultStr;

	private string visualLargerMultStr;

	private string visualSmallerMultStr;

	private string headPowLargeStr;

	private string headPowSmallStr;

	public BigSmallMod(ModContentPack content)
		: base(content)
	{
		if (settings == null)
		{
			settings = ((Mod)this).GetSettings<BSSettings>();
		}
		BSCacheExtensions.prepatched = ModsConfig.IsActive("zetrith.prepatcher");
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Expected O, but got Unknown
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		((Mod)this).DoSettingsWindowContents(inRect);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y + 35f, ((Rect)(ref inRect)).width, 35f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y + 30f, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 30f);
		Widgets.DrawMenuSection(val2);
		int num = tabKeys.Length;
		List<TabRecord> list = new List<TabRecord>();
		for (int i = 0; i < num; i++)
		{
			int tabIndex = i;
			list.Add(new TabRecord(TaggedString.op_Implicit(Translator.Translate(tabKeys[i])), (Action)delegate
			{
				selectedTab = tabIndex;
			}, selectedTab == tabIndex));
		}
		TabDrawer.DrawTabs<TabRecord>(val, list, 200f);
		Rect inRect2 = GenUI.ContractedBy(val2, 15f);
		columnWidth = ((Rect)(ref inRect2)).width - 20f;
		switch (selectedTab)
		{
		case 0:
			DrawGeneralTab(inRect2);
			break;
		case 1:
			DrawRacesTab(inRect2);
			break;
		case 2:
			DrawSizeTab(inRect2);
			break;
		case 3:
			DrawAutoCombat(inRect2);
			break;
		case 4:
			DrawExtrasTab(inRect2);
			break;
		case 5:
			DrawAdvancedTab(inRect2);
			break;
		case 6:
			DrawDeveloperTab(inRect2);
			break;
		}
	}

	private void BeginScrollArea(Rect inRect, ref Vector2 scrollPos, out Rect viewRect, float height = 600f)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		Rect val = inRect;
		viewRect = new Rect(0f, 0f, ((Rect)(ref val)).width - 20f, height);
		Widgets.BeginScrollView(val, ref scrollPos, viewRect, true);
	}

	private void EndScrollArea()
	{
		Widgets.EndScrollView();
	}

	private void DrawGeneralTab(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Expected O, but got Unknown
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0239: Unknown result type (might be due to invalid IL or missing references)
		//IL_0292: Unknown result type (might be due to invalid IL or missing references)
		//IL_02eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0339: Unknown result type (might be due to invalid IL or missing references)
		//IL_0392: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect);
		((Listing)val).Begin(viewRect);
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("BS_ResetCache")), (string)null, 1f))
		{
			List<Pawn> list = DictCache<Pawn, BSCache>.Cache.Keys.Select((Pawn x) => x).ToList();
			BigAndSmallCache.ScribedCache = new HashSet<BSCache>();
			BigAndSmallCache.refreshQueue.Clear();
			BigAndSmallCache.queuedJobs.Clear();
			BigAndSmallCache.schedulePostUpdate.Clear();
			BigAndSmallCache.scheduleFullUpdate.Clear();
			DictCache<Pawn, BSCache>.Cache = new ConcurrentDictionary<Pawn, BSCache>();
			Log.Message($"Reset Cache. Updating cache for {list.Count} pawns.");
			foreach (Pawn item in list.Where((Pawn x) => x != null && !((Thing)x).Discarded && !((Thing)x).Destroyed))
			{
				if (HumanoidPawnScaler.GetCache(item, forceRefresh: true) != null)
				{
					Log.Message($"Big and Small: Reset cache for {item}");
				}
			}
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("BS_ResetSettings")), (string)null, 1f))
		{
			settings.ResetToDefault();
		}
		if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("BS_ResetToRecommendedSettings")), (string)null, 1f))
		{
			settings.ResetToRecommended();
		}
		((Listing)val).GapLine(12f);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_GameMechanics")), -1f, (TipSignal?)null);
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_PreventUndead")), ref settings.preventUndead);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_InflitratorChance")), ref settings.inflitratorChance, ref inflitratorChanceStr, 0f, 1f, (float f) => $"{f * 100f:F1}%");
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_InflitratorRaidChance")), ref settings.inflitratorRaidChance, ref inflitratorRaidChanceStr, 0f, 1f, (float f) => $"{f * 100f:F1}%");
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_ImmortalReturnFactor")), ref settings.immortalReturnTimeFactor, ref immortalReturnFactorStr, 0.01f, 5f, (float f) => $"{f * 100f:F1}%");
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_SoulPowerFalloffOffset")), ref settings.soulPowerFalloffOffset, ref soulPowerFalloffOffsetStr, 0f, 20f, (float f) => $"{f:F1}");
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_SoulPowerGainMultiplier")), ref settings.soulPowerGainMultiplier, ref soulPowerGainMultiplierStr, 0.5f, 5f, (float f) => $"{f * 100f:F1}%");
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_MetabolismLimitOffset")), ref settings.metabolismLimits, ref metabolismLimitOffsetStr, 0f, 500f, (float f) => $"{f:F0}");
		((Listing)val).End();
		EndScrollArea();
	}

	private void DrawRacesTab(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Expected O, but got Unknown
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect);
		((Listing)val).Begin(viewRect);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_ToggleFeatures")), -1f, (TipSignal?)null);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_Surgery")), ref settings.surgeryAndBionics);
		((Listing)val).GapLine(12f);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_SapientSettings")), -1f, (TipSignal?)null);
		if (BigSmall.BSSapientAnimalsActive_ForcedByMods)
		{
			SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SapientAnimals_Forced")), ref settings.forcedOn, disabled: true);
		}
		else
		{
			SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SapientAnimals")), ref settings.sapientAnimals);
		}
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_AnimalsNoSkillPenalty")), ref settings.animalsLowSkillPenalty);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_AllAnimalsHaveHands")), ref settings.allAnimalsHaveHands);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SapientAnimalsCanRomanceAnySapientAnimals")), ref settings.animalOnAnimal);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SapientMechanoids")), ref settings.sapientMechanoids);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_SapientMechsMinAge")), ref settings.minAgeSapientMechs, ref sapientMechsMinAgeStr, 3f, 20f, (float f) => $"{f:F0}");
		((Listing)val).End();
		EndScrollArea();
	}

	private void DrawSizeTab(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Expected O, but got Unknown
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Expected O, but got Unknown
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Expected O, but got Unknown
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Expected O, but got Unknown
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Expected O, but got Unknown
		//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d0: Expected O, but got Unknown
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Expected O, but got Unknown
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0201: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Expected O, but got Unknown
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a3: Expected O, but got Unknown
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0313: Expected O, but got Unknown
		//IL_0313: Unknown result type (might be due to invalid IL or missing references)
		//IL_0319: Unknown result type (might be due to invalid IL or missing references)
		//IL_0324: Unknown result type (might be due to invalid IL or missing references)
		//IL_032a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0330: Unknown result type (might be due to invalid IL or missing references)
		//IL_0378: Expected O, but got Unknown
		//IL_0378: Unknown result type (might be due to invalid IL or missing references)
		//IL_0383: Unknown result type (might be due to invalid IL or missing references)
		//IL_0389: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a3: Expected O, but got Unknown
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect, 700f);
		((Listing)val).Begin(viewRect);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ScaleAnimals")), ref settings.scaleAnimals);
		((Listing)val).GapLine(12f);
		val.Label(Translator.Translate("BS_LowestUsed"), -1f, (string)null);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_MultDamageExplain")), ref settings.dmgExponent, ref dmgExpontentStr, 0f, 2f, (float f) => $"{f * 100f:F2}%");
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_FlatDMGExplain")), ref settings.flatDamageIncrease, ref flatDmtStr, 1f, 20f, (float f) => $"{f:F0}");
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_HungerMultiplierField")), ref settings.hungerRate, ref hungerMultStr, 0f, 1f, (float f) => $"{f * 100f:F0}%");
		((Listing)val).GapLine(12f);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_Rendering")), -1f, (TipSignal?)null);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SizeOffsetPawn")), ref settings.offsetBodyPos);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SizeOffsetAnimalPawn")), ref settings.offsetAnimalBodyPos);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_DisabeVFCachine")), ref settings.disableTextureCaching);
		val.Label(Translator.Translate("BS_ScalePawnDefault"), -1f, (string)null);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_ScaleLargerPawns")), ref settings.visualLargerMult, ref visualLargerMultStr, 0.05f, 20f, (float f) => $"{f:F2}");
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_ScaleSmallerPawns")), ref settings.visualSmallerMult, ref visualSmallerMultStr, 0.05f, 1f, (float f) => $"{f:F2}");
		((Listing)val).GapLine(12f);
		val.Label(Translator.Translate("BS_HeadSizeExplain"), -1f, (string)null);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_HeadExponentLargeField")), ref settings.headPowLarge, ref headPowLargeStr, -2f, 2f, (float f) => $"{f:F2}");
		val.Label(Translator.Translate("BS_HeadExponentSmallExplain"), -1f, (string)null);
		SettingsWidgets.CreateSettingsSlider(val, TaggedString.op_Implicit(Translator.Translate("BS_HeadExponentSmalleField")), ref settings.headPowSmall, ref headPowSmallStr, -1f, 2f, (float f) => $"{f:F2}");
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_NormalizeBodyType")), ref settings.scaleBodyTypes);
		((Listing)val).End();
		EndScrollArea();
	}

	private void DrawAutoCombat(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Expected O, but got Unknown
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Expected O, but got Unknown
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Expected O, but got Unknown
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Expected O, but got Unknown
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Expected O, but got Unknown
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Expected O, but got Unknown
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Expected O, but got Unknown
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Expected O, but got Unknown
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect);
		((Listing)val).Begin(viewRect);
		val.Label(Translator.Translate("BS_AutoCombatExplain"), -1f, (string)null);
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_EnabledDraftedJobs")), ref settings.enableDraftedJobs);
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_AutoCombatResets")), ref settings.autoCombatResets);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_LongChargeDefaultOff")), ref settings.autoCombatResetsLongCharge);
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowMeleeChargeBtn")), ref settings.showMeleeChargeBtn);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowTakeCoverBtn")), ref settings.showTakeCoverBtn);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_FullAIControl")), ref settings.showFullAIControlBtn);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowAutoUseAllAbilitiesBtn")), ref settings.showAutoUseAllAbilitiesBtn);
		SettingsWidgets.CreateRadioButtonsTwoOptions(val, TaggedString.op_Implicit(Translator.Translate("BS_RightClickAutoCombat")), ref settings.rightClickAutoCombatShowsMenu, TaggedString.op_Implicit(Translator.Translate("BS_RightClickAutoCombat_ShowMenu")), TaggedString.op_Implicit(Translator.Translate("BS_RightClickAutoCombat_Toggle")));
		((Listing)val).End();
		EndScrollArea();
	}

	private void DrawExtrasTab(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Expected O, but got Unknown
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect);
		((Listing)val).Begin(viewRect);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ForceDisableExtraUIWidgets")), ref settings.disableExtraWidgets);
		if (settings.disableExtraWidgets)
		{
			((Listing)val).GapLine(12f);
			val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_ExtraUIForceDisabledWarning")), -1f, (TipSignal?)null);
		}
		if (!settings.disableExtraWidgets)
		{
			if (BigSmall.BSGenesActive || GlobalSettings.IsFeatureEnabled("RecolorButton"))
			{
				SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowColorPaletteBtn_Forced")), ref settings.forcedOn, disabled: true);
			}
			else
			{
				SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowColorPaletteBtn")), ref settings.showClrPaletteBtn);
			}
			if (BigSmall.BSGenesActive || GlobalSettings.IsFeatureEnabled("RaceButton"))
			{
				SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowRaceBtn_Forced")), ref settings.forcedOn, disabled: true);
			}
			else
			{
				SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ShowRaceBtn")), ref settings.showRaceBtn);
			}
		}
		((Listing)val).GapLine(12f);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_SciFiNames")), ref settings.useSciFiNames);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_FantasyNames")), ref settings.useFantasyNames);
		((Listing)val).End();
		EndScrollArea();
	}

	private void DrawAdvancedTab(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Expected O, but got Unknown
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Expected O, but got Unknown
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Expected O, but got Unknown
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect);
		((Listing)val).Begin(viewRect);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_RecolourAnything")), -1f, (TipSignal?)null);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_MakeBionicsAndGenesRecolourable")), ref settings.makeDefsRecolorable);
		((Listing)val).GapLine(12f);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_ActivateExperimental")), -1f, (TipSignal?)null);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_ActivateExperimental")), ref settings.experimental);
		((Listing)val).GapLine(12f);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_GenesSpecific")), -1f, (TipSignal?)null);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_DoDefGeneration")), ref settings.generateDefs);
		((Listing)val).End();
		EndScrollArea();
	}

	private void DrawDeveloperTab(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Expected O, but got Unknown
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Expected O, but got Unknown
		Listing_Standard val = new Listing_Standard
		{
			ColumnWidth = columnWidth
		};
		BeginScrollArea(inRect, ref scrollPosition, out var viewRect);
		((Listing)val).Begin(viewRect);
		val.Label(ColoredText.AsTipTitle(Translator.Translate("BS_DevSettings")), -1f, (TipSignal?)null);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_JesusMode")), ref settings.jesusMode);
		SettingsWidgets.CreateSettingCheckbox(val, TaggedString.op_Implicit(Translator.Translate("BS_RecruitDevSpawned")), ref settings.recruitDevSpawned);
		((Listing)val).End();
		EndScrollArea();
	}

	public override string SettingsCategory()
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(Translator.Translate("BS_BigAndSmall"));
	}
}
