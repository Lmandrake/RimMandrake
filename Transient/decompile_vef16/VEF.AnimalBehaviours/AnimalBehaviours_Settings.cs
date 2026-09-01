using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class AnimalBehaviours_Settings : ModSettings
{
	public static bool flagCorpseDecayingEffect = true;

	public static bool flagDigWhenHungry = true;

	public static bool flagAnimalParticles = true;

	public static bool flagAsexualReproduction = true;

	public static bool flagBlinkMechanics = true;

	public static bool flagBuildPeriodically = true;

	public static bool flagDigPeriodically = true;

	public static bool flagChargeBatteries = true;

	public static bool flagExplodingAnimalEggs = true;

	public static bool flagHovering = true;

	public static bool flagGraphicChanging = true;

	public static bool flagEffecters = true;

	public static bool flagRegeneration = true;

	public static bool flagResurrection = true;

	public static bool flagUntameable = true;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Values.Look<bool>(ref flagCorpseDecayingEffect, "flagCorpseDecayingEffect", true, true);
		Scribe_Values.Look<bool>(ref flagDigWhenHungry, "flagDigWhenHungry", true, true);
		Scribe_Values.Look<bool>(ref flagAnimalParticles, "flagAnimalParticles", true, true);
		Scribe_Values.Look<bool>(ref flagAsexualReproduction, "flagAsexualReproduction", true, true);
		Scribe_Values.Look<bool>(ref flagBlinkMechanics, "flagBlinkMechanics", true, true);
		Scribe_Values.Look<bool>(ref flagBuildPeriodically, "flagBuildPeriodically", true, true);
		Scribe_Values.Look<bool>(ref flagDigPeriodically, "flagDigPeriodically", true, true);
		Scribe_Values.Look<bool>(ref flagChargeBatteries, "flagChargeBatteries", true, true);
		Scribe_Values.Look<bool>(ref flagExplodingAnimalEggs, "flagExplodingAnimalEggs", true, true);
		Scribe_Values.Look<bool>(ref flagHovering, "flagHovering", true, true);
		Scribe_Values.Look<bool>(ref flagGraphicChanging, "flagGraphicChanging", true, true);
		Scribe_Values.Look<bool>(ref flagEffecters, "flagEffecters", true, true);
		Scribe_Values.Look<bool>(ref flagRegeneration, "flagRegeneration", true, true);
		Scribe_Values.Look<bool>(ref flagResurrection, "flagResurrection", true, true);
		Scribe_Values.Look<bool>(ref flagUntameable, "flagUntameable", true, true);
	}

	public static void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_0143: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_0173: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0184: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		//IL_020e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0214: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		//IL_023e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Unknown result type (might be due to invalid IL or missing references)
		//IL_0263: Unknown result type (might be due to invalid IL or missing references)
		//IL_026e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f3: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		val.Label(Translator.Translate("VCE_AffectsAllAnimalMods"), -1f, (string)null);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_CorpseDecayingEffectOption")), ref flagCorpseDecayingEffect, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_DigWhenHungryOption")), ref flagDigWhenHungry, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_DigPeriodicallyOption")), ref flagDigPeriodically, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_AnimalParticlesOption")), ref flagAnimalParticles, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_AsexualReproductionOption")), ref flagAsexualReproduction, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_BlinkMechanicsOption")), ref flagBlinkMechanics, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_BuildPeriodicallyOption")), ref flagBuildPeriodically, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_ChargeBatteriesOption")), ref flagChargeBatteries, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_ExplodingEggsOption")), ref flagExplodingAnimalEggs, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_HoveringOption")), ref flagHovering, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_GraphicChangingOption")), ref flagGraphicChanging, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_EffecterOption")), ref flagEffecters, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_RegenerationOption")), ref flagRegeneration, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_ResurrectionOption")), ref flagResurrection, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("VCE_UntameableOption")), ref flagUntameable, (string)null, 0f, 1f);
		((Listing)val).Gap(12f);
		((Listing)val).End();
	}
}
