using System;
using BigAndSmall.SimpleCustomRaces;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[StaticConstructorOnStartup]
public static class BSCore
{
	private static readonly Type patchType;

	public static Harmony harmony;

	static BSCore()
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Expected O, but got Unknown
		harmony = new Harmony("RedMattis.BetterPrerequisites");
		if (Type.GetType("RimWorld.CompAbilityEffect_RequiresTrainable") != null)
		{
			Log.Error("Did not find the Ludeon comp CompAbilityEffect_RequiresTrainable. This likely means your rimworld version is outdated and will crash in a moment.");
		}
		patchType = typeof(BSCore);
		harmony.PatchAll();
		PregnancyPatches.ApplyPatches();
		if (NalsToggles.FALoaded)
		{
			NalsToggles.ApplyNLPatches(harmony);
		}
		VanillaExpanded.PatchVanillaExpanded(harmony);
	}

	public static void RunBeforeGenerateImpliedDefs(bool hotReload)
	{
		if (!hotReload)
		{
			GlobalSettings.Initialize();
		}
		UpdateLegacyPawnExts();
		ConditionalGraphic.ResetStaticData();
		DefAltNamer.Initialize();
		NewFoodCategory.SetupFoodCategories();
		HumanPatcher.MechanicalSetup();
		RaceFuser.PreHotreload();
		RaceFuser.CreateMergedBodyTypes(hotReload);
		HumanlikeAnimalGenerator.GenerateHumanlikeAnimals(hotReload);
		FlagStringData.Setup(force: true);
		BSInheritanceWrapper.TrySetup();
	}

	private static void UpdateLegacyPawnExts()
	{
		try
		{
			foreach (GeneDef allDef in DefDatabase<GeneDef>.AllDefs)
			{
				foreach (PawnExtension item in allDef.GetAllPawnExtensionsOnGene())
				{
					item.UpdateLegacy();
				}
			}
		}
		catch (Exception ex)
		{
			Log.Warning($"[Big and Small] Exception while updating legacy pawn extensions: {ex}. Some legacy data may not work as expected.\n\n{ex.StackTrace}");
		}
	}

	public static void RunDuringGenerateImpliedDefs(bool hotReload)
	{
		GeneDefPatcher.PatchExistingDefs();
		RaceFuser.GenerateCorpses(hotReload);
		if (!hotReload)
		{
			HumanPatcher.MechanicalCorpseSetup();
		}
		XenotypeDefPatcher.PatchDefs();
		ModDefPatcher.PatchDefs();
		HumanPatcher.PatchRecipes();
		ThoughtDefPatcher.PatchDefs();
		_ = BigSmallMod.settings.experimental;
	}

	public static void RunAfterGenerateImpliedDefs(bool hotReload)
	{
		foreach (ThingDef key in HumanlikeAnimalGenerator.humanlikeAnimals.Keys)
		{
			ThingDef corpseDef = key.race.corpseDef;
			if (corpseDef != null)
			{
				corpseDef.thingCategories.Clear();
				corpseDef.thingCategories.Add(BSDefs.BS_CorpsesHumanlikeAnimals);
			}
		}
		foreach (ThingDef key2 in FusedBody.FusedBodyByThing.Keys)
		{
			ThingDef corpseDef2 = key2.race.corpseDef;
			if (corpseDef2 != null)
			{
				corpseDef2.thingCategories.Clear();
				corpseDef2.thingCategories.Add(BSDefs.BS_CorpsesHumanlikeHybrids);
			}
		}
		try
		{
			RenderNodePatcher.TryPatchPawnRenderNodeDefs();
		}
		catch (Exception ex)
		{
			Log.Error($"[Big and Small] Exception while patching RenderNodeDefs: {ex} {ex.StackTrace}");
		}
	}
}
