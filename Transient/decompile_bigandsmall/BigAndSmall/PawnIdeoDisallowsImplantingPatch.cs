using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Xenogerm), "PawnIdeoDisallowsImplanting")]
public static class PawnIdeoDisallowsImplantingPatch
{
	public static void Postfix(ref bool __result, Pawn selPawn)
	{
		if (selPawn?.needs != null && HumanoidPawnScaler.GetCache(selPawn) != null && GeneHelpers.GetActiveGenesByName(selPawn, "BS_NoXenogerms").Count() > 0)
		{
			__result = true;
		}
	}
}
