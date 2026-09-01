using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(CompPowerPlantWater), "CompTick")]
public static class VanillaExpandedFramework_CompPowerPlantWater_CompTick_Patch
{
	public static float cachedGameConditionMultiplier = 1f;

	[HarmonyPostfix]
	public static void PostFix(CompPowerPlantWater __instance)
	{
		if (!Gen.IsHashIntervalTick((Thing)(object)((ThingComp)__instance).parent, 2000))
		{
			return;
		}
		cachedGameConditionMultiplier = 1f;
		if (((Thing)((ThingComp)__instance).parent).Map == null || ((Thing)((ThingComp)__instance).parent).Map.gameConditionManager.ActiveConditions.Count <= 0)
		{
			return;
		}
		foreach (GameCondition activeCondition in ((Thing)((ThingComp)__instance).parent).Map.gameConditionManager.ActiveConditions)
		{
			MapConditionExtension modExtension = ((Def)activeCondition.def).GetModExtension<MapConditionExtension>();
			if (modExtension != null)
			{
				cachedGameConditionMultiplier *= modExtension.watermillStrengthMultiplier;
			}
		}
	}
}
