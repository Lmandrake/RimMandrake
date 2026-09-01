using HarmonyLib;
using RimWorld;

namespace VEF.Abilities;

[HarmonyPatch(typeof(PawnFlyer), "RecomputePosition")]
public static class VanillaExpandedFramework_PawnFlyer_RecomputePosition_Patch
{
	public static bool Prefix(PawnFlyer __instance)
	{
		if (__instance is AbilityPawnFlyer abilityPawnFlyer)
		{
			return !abilityPawnFlyer.CustomRecomputePosition();
		}
		return true;
	}
}
