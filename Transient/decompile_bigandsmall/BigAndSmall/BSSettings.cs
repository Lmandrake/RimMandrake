using UnityEngine;
using Verse;

namespace BigAndSmall;

public class BSSettings : ModSettings
{
	public bool forcedOn = true;

	public bool forcedOff;

	private static readonly bool defaultGenerateDefs = true;

	public bool generateDefs = defaultGenerateDefs;

	private static readonly bool defaultPathRacesFromOtherMods = true;

	public bool pathRacesFromOtherMods = defaultPathRacesFromOtherMods;

	private static readonly bool defaultMakeDefsRecolorable = false;

	public bool makeDefsRecolorable = defaultMakeDefsRecolorable;

	private static readonly bool defaultExperimental = false;

	public bool experimental = defaultExperimental;

	private static readonly bool defaultSapientAnimals = false;

	public bool sapientAnimals = defaultSapientAnimals;

	private static readonly float defaultSapientAnimalsChance = 0f;

	public float sapientAnimalsChance = defaultSapientAnimalsChance;

	private static readonly bool defaultSapientMechanoids = false;

	public bool sapientMechanoids = defaultSapientMechanoids;

	public static readonly float minAgeSapientMechsDefault = 13f;

	public float minAgeSapientMechs = minAgeSapientMechsDefault;

	private static readonly bool defaultSurgeryAndBionics = true;

	public bool surgeryAndBionics = defaultSurgeryAndBionics;

	private static readonly float defaultVisualLargerMult = 1f;

	public float visualLargerMult = defaultVisualLargerMult;

	private static readonly float defaultVisualSmallerMult = 1f;

	public float visualSmallerMult = defaultVisualSmallerMult;

	private static readonly float defaultHeadPowLarge = 0.8f;

	public float headPowLarge = defaultHeadPowLarge;

	private static readonly float defaultHeadPowSmall = 0.65f;

	public float headPowSmall = defaultHeadPowSmall;

	private static readonly float defaultDmgExponent = 0.75f;

	public float dmgExponent = defaultDmgExponent;

	private static readonly float defaultFlatDmgIncrease = 8f;

	public float flatDamageIncrease = defaultFlatDmgIncrease;

	private static readonly float defaultHungerRate = 1f;

	public float hungerRate = defaultHungerRate;

	private static readonly bool defaultScaleBT = false;

	public bool scaleBodyTypes = defaultScaleBT;

	private static readonly bool defaultScaleAnimals = true;

	public bool scaleAnimals = defaultScaleAnimals;

	private static readonly bool defaultDisableTextureCaching = true;

	public bool disableTextureCaching = defaultDisableTextureCaching;

	private static readonly bool defaultRealTimeUpdates = false;

	public bool realTimeUpdates = defaultRealTimeUpdates;

	private static readonly bool defaultOffsetBodyPos = true;

	public bool offsetBodyPos = defaultOffsetBodyPos;

	private static readonly bool defaultOffsetAnimalBodyPos = true;

	public bool offsetAnimalBodyPos = defaultOffsetAnimalBodyPos;

	private static readonly bool defaultPatchPlayerFactions = true;

	public bool patchPlayerFactions = defaultPatchPlayerFactions;

	public static readonly bool defaultPreventUndead = false;

	public bool preventUndead = defaultPreventUndead;

	public static readonly bool defaultUseSciFiNaming = false;

	public bool useSciFiNames = defaultUseSciFiNaming;

	public static readonly bool defaultUseFantasyNaming = false;

	public bool useFantasyNames = defaultUseFantasyNaming;

	public static readonly float inflitratorChanceDefault = 0.01f;

	public float inflitratorChance = inflitratorChanceDefault;

	public static readonly float inflitratorRaidChanceDefault = 0.005f;

	public float inflitratorRaidChance = inflitratorRaidChanceDefault;

	public static readonly float immortalReturnTimeFactorDefault = 1f;

	public float immortalReturnTimeFactor = immortalReturnTimeFactorDefault;

	public static readonly float soulPowerFalloffOffsetDefault = 0f;

	public float soulPowerFalloffOffset = soulPowerFalloffOffsetDefault;

	public static readonly float metabolismLimitDefault = 0f;

	public float metabolismLimits = metabolismLimitDefault;

	public static readonly float soulPowerGainMultiplierDefault = 1f;

	public float soulPowerGainMultiplier = soulPowerGainMultiplierDefault;

	private static readonly bool defaultAllAnimalsHaveHands = false;

	public bool allAnimalsHaveHands = defaultAllAnimalsHaveHands;

	private static readonly bool defaultAnimalOnAnimal = false;

	public bool animalOnAnimal = defaultAnimalOnAnimal;

	private static readonly bool defaultAnimalsLowSkillPenalty = false;

	public bool animalsLowSkillPenalty = defaultAnimalsLowSkillPenalty;

	private static readonly bool defaultEnableDraftedJobs = false;

	public bool enableDraftedJobs = defaultEnableDraftedJobs;

	public static readonly bool defaultAutoCombatResets = false;

	public bool autoCombatResets = defaultAutoCombatResets;

	public static readonly bool defaultAutoCombatResetsLongCharge = false;

	public bool autoCombatResetsLongCharge = defaultAutoCombatResetsLongCharge;

	public static readonly bool defaultShowMeleeChargeBtn = true;

	public bool showMeleeChargeBtn = defaultShowMeleeChargeBtn;

	public static readonly bool defaultShowTakeCoverBtn = true;

	public bool showTakeCoverBtn = defaultShowTakeCoverBtn;

	public static readonly bool defaultShowFullAiControlBtn = true;

	public bool showFullAIControlBtn = defaultShowFullAiControlBtn;

	public static readonly bool defaultShowAutoUseAllAbilitiesBtn = true;

	public bool showAutoUseAllAbilitiesBtn = defaultShowAutoUseAllAbilitiesBtn;

	public static readonly bool defaultRightClickAutoCombatShowsMenu = false;

	public bool rightClickAutoCombatShowsMenu = defaultRightClickAutoCombatShowsMenu;

	private static readonly bool defaultShowClrPaletteBtn = false;

	public bool showClrPaletteBtn = defaultShowClrPaletteBtn;

	private static readonly bool defaultShowRaceBtn = false;

	public bool showRaceBtn = defaultShowRaceBtn;

	public static readonly bool defaultDisableExtraWidgets = false;

	public bool disableExtraWidgets = defaultDisableExtraWidgets;

	public static readonly bool defaultJesusMode = false;

	public bool jesusMode = defaultJesusMode;

	public static readonly bool defaultRecruitDevSpawned = true;

	public bool recruitDevSpawned = defaultRecruitDevSpawned;

	public int MetabolismLimit => Mathf.RoundToInt(metabolismLimits);

	public bool GetAndroidsEnabled()
	{
		if (!sapientMechanoids && !ModsConfig.IsActive("RedMattis.BigSmall.SimpleAndroids"))
		{
			return ModsConfig.IsActive("RedMattis.BigSmall.Core");
		}
		return true;
	}

	public override void ExposeData()
	{
		Scribe_Values.Look<bool>(ref preventUndead, "preventUndead", defaultPreventUndead, false);
		Scribe_Values.Look<float>(ref inflitratorChance, "inflitratorChance", inflitratorChanceDefault, false);
		Scribe_Values.Look<float>(ref inflitratorRaidChance, "inflitratorRaidChance", inflitratorRaidChanceDefault, false);
		Scribe_Values.Look<float>(ref immortalReturnTimeFactor, "immortalReturnTimeFactor", immortalReturnTimeFactorDefault, false);
		Scribe_Values.Look<float>(ref soulPowerFalloffOffset, "soulPowerFalloffOffset", soulPowerFalloffOffsetDefault, false);
		Scribe_Values.Look<float>(ref soulPowerGainMultiplier, "soulPowerGainMultiplier", soulPowerGainMultiplierDefault, false);
		Scribe_Values.Look<float>(ref metabolismLimits, "metabolismLimits", metabolismLimitDefault, false);
		Scribe_Values.Look<bool>(ref surgeryAndBionics, "surgeryAndBionics", defaultSurgeryAndBionics, false);
		Scribe_Values.Look<bool>(ref sapientAnimals, "sapientAnimals", defaultSapientAnimals, false);
		Scribe_Values.Look<float>(ref sapientAnimalsChance, "sapientAnimalsChance", defaultSapientAnimalsChance, false);
		Scribe_Values.Look<bool>(ref sapientMechanoids, "sapientMechanoids", defaultSapientMechanoids, false);
		Scribe_Values.Look<float>(ref minAgeSapientMechs, "sapientMechanoidsMinAge", minAgeSapientMechsDefault, false);
		Scribe_Values.Look<bool>(ref allAnimalsHaveHands, "allAnimalsHaveHands", defaultAllAnimalsHaveHands, false);
		Scribe_Values.Look<bool>(ref animalOnAnimal, "sapientAnimalsCanRomanceAnySapientAnimals", defaultAnimalOnAnimal, false);
		Scribe_Values.Look<bool>(ref animalsLowSkillPenalty, "animalsNoSkillPenalty", defaultAnimalsLowSkillPenalty, false);
		Scribe_Values.Look<bool>(ref scaleAnimals, "scaleAnimals", defaultScaleAnimals, false);
		Scribe_Values.Look<float>(ref dmgExponent, "dmgExponent", defaultDmgExponent, false);
		Scribe_Values.Look<float>(ref flatDamageIncrease, "flatDmgIncrease", defaultFlatDmgIncrease, false);
		Scribe_Values.Look<float>(ref hungerRate, "hungerRate", defaultHungerRate, false);
		Scribe_Values.Look<bool>(ref offsetBodyPos, "offsetBodyPos", defaultOffsetBodyPos, false);
		Scribe_Values.Look<bool>(ref offsetAnimalBodyPos, "offsetAnimalBodyPos", defaultOffsetAnimalBodyPos, false);
		Scribe_Values.Look<bool>(ref disableTextureCaching, "disableBSTextureCaching", defaultDisableTextureCaching, false);
		Scribe_Values.Look<float>(ref visualLargerMult, "visualLargerMult", defaultVisualLargerMult, false);
		Scribe_Values.Look<float>(ref visualSmallerMult, "visualSmallerMult", defaultVisualSmallerMult, false);
		Scribe_Values.Look<float>(ref headPowLarge, "headPowLarge", defaultHeadPowLarge, false);
		Scribe_Values.Look<float>(ref headPowSmall, "headPowSmall2", defaultHeadPowSmall, false);
		Scribe_Values.Look<bool>(ref scaleBodyTypes, "scaleBt", defaultScaleBT, false);
		Scribe_Values.Look<bool>(ref enableDraftedJobs, "enableDraftedJobs", defaultEnableDraftedJobs, false);
		Scribe_Values.Look<bool>(ref autoCombatResets, "autoCombatResets", defaultAutoCombatResets, false);
		Scribe_Values.Look<bool>(ref autoCombatResetsLongCharge, "autoCombatResetsLongCharge", defaultAutoCombatResetsLongCharge, false);
		Scribe_Values.Look<bool>(ref showMeleeChargeBtn, "showMeleeChargeBtn", defaultShowMeleeChargeBtn, false);
		Scribe_Values.Look<bool>(ref showTakeCoverBtn, "showTakeCoverBtn", defaultShowTakeCoverBtn, false);
		Scribe_Values.Look<bool>(ref showFullAIControlBtn, "showFullAiControlBtn", defaultShowFullAiControlBtn, false);
		Scribe_Values.Look<bool>(ref showAutoUseAllAbilitiesBtn, "showAutoUseAllAbilitiesBtn", defaultShowAutoUseAllAbilitiesBtn, false);
		Scribe_Values.Look<bool>(ref rightClickAutoCombatShowsMenu, "rightClickAutoCombatShowsMenu", defaultRightClickAutoCombatShowsMenu, false);
		Scribe_Values.Look<bool>(ref showClrPaletteBtn, "showClrPaletteBtn", defaultShowClrPaletteBtn, false);
		Scribe_Values.Look<bool>(ref showRaceBtn, "showRaceBtn", defaultShowRaceBtn, false);
		Scribe_Values.Look<bool>(ref disableExtraWidgets, "disableExtraWidgets", defaultDisableExtraWidgets, false);
		Scribe_Values.Look<bool>(ref useSciFiNames, "useSciFiNames", defaultUseSciFiNaming, false);
		Scribe_Values.Look<bool>(ref useFantasyNames, "useFantasyNames", defaultUseFantasyNaming, false);
		Scribe_Values.Look<bool>(ref experimental, "experimental", defaultExperimental, false);
		Scribe_Values.Look<bool>(ref makeDefsRecolorable, "makeDefsRecolorable", defaultMakeDefsRecolorable, false);
		Scribe_Values.Look<bool>(ref pathRacesFromOtherMods, "pathRacesFromOtherMods", defaultPathRacesFromOtherMods, false);
		Scribe_Values.Look<bool>(ref generateDefs, "generateDefs", defaultGenerateDefs, false);
		Scribe_Values.Look<bool>(ref jesusMode, "jesusMode", defaultJesusMode, false);
		Scribe_Values.Look<bool>(ref recruitDevSpawned, "recruitDevSpawned", defaultRecruitDevSpawned, false);
		Scribe_Values.Look<bool>(ref patchPlayerFactions, "patchPlayerFactions", defaultPatchPlayerFactions, false);
		Scribe_Values.Look<bool>(ref realTimeUpdates, "realTimeUpdates", defaultRealTimeUpdates, false);
		((ModSettings)this).ExposeData();
	}

	public void ResetToDefault()
	{
		preventUndead = defaultPreventUndead;
		inflitratorChance = inflitratorChanceDefault;
		inflitratorRaidChance = inflitratorRaidChanceDefault;
		immortalReturnTimeFactor = immortalReturnTimeFactorDefault;
		soulPowerFalloffOffset = soulPowerFalloffOffsetDefault;
		soulPowerGainMultiplier = soulPowerGainMultiplierDefault;
		metabolismLimits = metabolismLimitDefault;
		surgeryAndBionics = defaultSurgeryAndBionics;
		sapientAnimals = defaultSapientAnimals;
		sapientAnimalsChance = defaultSapientAnimalsChance;
		sapientMechanoids = defaultSapientMechanoids;
		minAgeSapientMechs = minAgeSapientMechsDefault;
		allAnimalsHaveHands = defaultAllAnimalsHaveHands;
		animalOnAnimal = defaultAnimalOnAnimal;
		animalsLowSkillPenalty = defaultAnimalsLowSkillPenalty;
		scaleAnimals = defaultScaleAnimals;
		dmgExponent = defaultDmgExponent;
		flatDamageIncrease = defaultFlatDmgIncrease;
		hungerRate = defaultHungerRate;
		offsetBodyPos = defaultOffsetBodyPos;
		offsetAnimalBodyPos = defaultOffsetAnimalBodyPos;
		disableTextureCaching = defaultDisableTextureCaching;
		visualLargerMult = defaultVisualLargerMult;
		visualSmallerMult = defaultVisualSmallerMult;
		headPowLarge = defaultHeadPowLarge;
		headPowSmall = defaultHeadPowSmall;
		scaleBodyTypes = defaultScaleBT;
		enableDraftedJobs = defaultEnableDraftedJobs;
		autoCombatResets = defaultAutoCombatResets;
		showMeleeChargeBtn = defaultShowMeleeChargeBtn;
		showTakeCoverBtn = defaultShowTakeCoverBtn;
		showAutoUseAllAbilitiesBtn = defaultShowAutoUseAllAbilitiesBtn;
		rightClickAutoCombatShowsMenu = defaultRightClickAutoCombatShowsMenu;
		showClrPaletteBtn = defaultShowClrPaletteBtn;
		showRaceBtn = defaultShowRaceBtn;
		disableExtraWidgets = defaultDisableExtraWidgets;
		useSciFiNames = defaultUseSciFiNaming;
		useFantasyNames = defaultUseFantasyNaming;
		experimental = defaultExperimental;
		makeDefsRecolorable = defaultMakeDefsRecolorable;
		pathRacesFromOtherMods = defaultPathRacesFromOtherMods;
		generateDefs = defaultGenerateDefs;
		jesusMode = defaultJesusMode;
		recruitDevSpawned = defaultRecruitDevSpawned;
		patchPlayerFactions = defaultPatchPlayerFactions;
		realTimeUpdates = defaultRealTimeUpdates;
	}

	public void ResetToRecommended()
	{
		ResetToDefault();
		scaleBodyTypes = true;
		enableDraftedJobs = true;
	}
}
