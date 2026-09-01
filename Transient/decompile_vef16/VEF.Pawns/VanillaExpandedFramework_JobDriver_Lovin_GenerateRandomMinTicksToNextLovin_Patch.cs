using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(JobDriver_Lovin))]
[HarmonyPatch("GenerateRandomMinTicksToNextLovin")]
public static class VanillaExpandedFramework_JobDriver_Lovin_GenerateRandomMinTicksToNextLovin_Patch
{
	[HarmonyPostfix]
	public static void ModifyMTB(ref int __result, Pawn pawn)
	{
		__result = (int)((float)__result * StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_MTBLovinFactor, true, -1));
	}
}
