using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn), "PostMapInit")]
public static class Pawn_PostMapInit
{
	public static void Postfix(Pawn __instance)
	{
		RefreshPawnGenes(__instance);
		BSCache cache = HumanoidPawnScaler.GetCache(__instance);
		if (cache != null)
		{
			List<PawnExtension> allPawnExtensions = __instance.GetAllPawnExtensions();
			cache.HandleSkillsAndAptitudes(allPawnExtensions);
		}
	}

	public static void RefreshPawnGenes(Pawn __instance, bool forceRefresh = true)
	{
		if (__instance != null)
		{
			GenderMethods.UpdatePawnHairAndHeads(__instance);
			if (forceRefresh)
			{
				HumanoidPawnScaler.GetCache(__instance, forceRefresh: true);
			}
		}
		else
		{
			Log.Error("BetterPrerequisites: Someone just called PostMapInit called with null pawn. Probably someone did a whoopsie!");
		}
	}
}
