using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(GeneUtility), "IsBloodfeeder")]
public static class IsBloodfeederPatch
{
	public static void Postfix(ref bool __result, Pawn pawn)
	{
		if (!__result && pawn?.needs != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null)
			{
				__result = cache.isBloodFeeder;
			}
		}
	}

	public static bool IsBloodfeeder(Pawn pawn)
	{
		if (pawn.RaceProps.Humanlike && (pawn.needs != null || pawn.Dead) && pawn.genes != null)
		{
			List<string> geneNames = new List<string> { "VU_WhiteRoseBite", "VU_DraculBite", "VU_SuccubusBloodFeeder" };
			if (GeneHelpers.GetActiveGenesByNames(pawn, geneNames).Count() > 0)
			{
				return true;
			}
		}
		return false;
	}
}
