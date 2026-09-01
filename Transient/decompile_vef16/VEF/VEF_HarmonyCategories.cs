using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using VEF.Apparels;
using VEF.Genes;
using VEF.Hediffs;
using VEF.Things;
using Verse;

namespace VEF;

public class VEF_HarmonyCategories
{
	public const string LateHarmonyPatchCategory = "LateHarmonyPatch";

	public const string MoveSpeedFactorByTerrainTagCategory = "MoveSpeedFactorByTerrainTag";

	public const string UseStoneChunksAsStuffInRecipes = "UseStoneChunksAsStuffInRecipes";

	internal static void TryPatchAll(Harmony harmony)
	{
		try
		{
			harmony.PatchAllUncategorized();
		}
		catch (Exception arg)
		{
			Log.Error($"[VEF] Failed running uncategorized patches:\n{arg}");
		}
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			RunPatches(harmony, "LateHarmonyPatch");
			RunPatches(harmony, "MoveSpeedFactorByTerrainTag", IsMoveSpeedFactorByTerrainTagActive);
			RunPatches(harmony, "UseStoneChunksAsStuffInRecipes", IsStoneChunksAsStuffInRecipesActive);
		});
	}

	private static void RunPatches(Harmony harmony, string patchCategory, Func<bool> validator = null)
	{
		try
		{
			if (validator == null || validator())
			{
				harmony.PatchCategory(patchCategory);
			}
		}
		catch (Exception arg)
		{
			Log.Error($"[VEF] Failed running patches from category '{patchCategory}':\n{arg}");
		}
	}

	private static bool IsMoveSpeedFactorByTerrainTagActive()
	{
		foreach (GeneDef allDef in DefDatabase<GeneDef>.AllDefs)
		{
			GeneExtension modExtension = ((Def)allDef).GetModExtension<GeneExtension>();
			if (modExtension != null && IsThereAnyTerrainWithTag(modExtension.moveSpeedFactorByTerrainTag))
			{
				return true;
			}
		}
		foreach (HediffDef allDef2 in DefDatabase<HediffDef>.AllDefs)
		{
			HediffCompProperties_MoveSpeedFactorByTerrainTag hediffCompProperties_MoveSpeedFactorByTerrainTag = allDef2.CompProps<HediffCompProperties_MoveSpeedFactorByTerrainTag>();
			if (hediffCompProperties_MoveSpeedFactorByTerrainTag != null && IsThereAnyTerrainWithTag(hediffCompProperties_MoveSpeedFactorByTerrainTag.moveSpeedFactorByTerrainTag))
			{
				return true;
			}
		}
		foreach (ThingDef allDef3 in DefDatabase<ThingDef>.AllDefs)
		{
			ApparelExtension modExtension2 = ((Def)allDef3).GetModExtension<ApparelExtension>();
			if (modExtension2 != null && IsThereAnyTerrainWithTag(modExtension2.moveSpeedFactorByTerrainTag))
			{
				return true;
			}
		}
		return false;
		static bool IsThereAnyTerrainWithTag(Dictionary<string, List<MoveSpeedFactor>> moveSpeedFactorByTerrainTag)
		{
			if (GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(moveSpeedFactorByTerrainTag))
			{
				return false;
			}
			foreach (string tag in moveSpeedFactorByTerrainTag.Keys)
			{
				if (DefDatabase<TerrainDef>.AllDefs.Any((TerrainDef terrain) => terrain.tags != null && terrain.tags.Contains(tag)))
				{
					return true;
				}
			}
			return false;
		}
	}

	private static bool IsStoneChunksAsStuffInRecipesActive()
	{
		foreach (RecipeDef allDef in DefDatabase<RecipeDef>.AllDefs)
		{
			RecipeExtension modExtension = ((Def)allDef).GetModExtension<RecipeExtension>();
			if (modExtension != null && modExtension.chunksAsStuff)
			{
				return true;
			}
		}
		return false;
	}
}
