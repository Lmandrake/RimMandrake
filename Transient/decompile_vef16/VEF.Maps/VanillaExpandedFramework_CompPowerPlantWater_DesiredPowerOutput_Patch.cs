using HarmonyLib;

namespace VEF.Maps;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_CompPowerPlantWater_DesiredPowerOutput_Patch
{
	[HarmonyPostfix]
	public static void PostFix(ref float __result)
	{
		__result *= VanillaExpandedFramework_CompPowerPlantWater_CompTick_Patch.cachedGameConditionMultiplier;
	}
}
