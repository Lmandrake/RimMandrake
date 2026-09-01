using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class GenderAndSexPatches
{
	[HarmonyPatch(typeof(StatPart_FertilityByGenderAge), "AgeFactor")]
	[HarmonyPostfix]
	public static void EveryFertileFix(ref float __result, Pawn pawn)
	{
		if (pawn.needs != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null && cache.everFertile && __result < 1f)
			{
				__result = 1f;
			}
		}
		new List<string> { "VPECurses_VPECurse_Curse1", "VPECurses_VPECurse_Suffering2", "VPECurses_VPECurse_Misfortune99" };
		foreach (Hediff item in pawn.health.hediffSet.hediffs.Where((Hediff x) => ((Def)x.def).defName == "VPECurses_VPECurse_Curse1"))
		{
			pawn.health.RemoveHediff(item);
		}
	}

	[HarmonyPatch(typeof(PawnUtility), "BodyResourceGrowthSpeed")]
	public static void Postfix(ref float __result, Pawn pawn)
	{
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null)
		{
			__result *= cache.pregnancySpeed;
		}
	}
}
