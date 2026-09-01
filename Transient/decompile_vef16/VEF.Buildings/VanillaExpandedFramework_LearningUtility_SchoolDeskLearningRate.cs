using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(LearningUtility), "SchoolDeskLearningRate")]
public static class VanillaExpandedFramework_LearningUtility_SchoolDeskLearningRate
{
	public static bool Prefix(Thing schoolDesk, ref float __result)
	{
		__result = StatExtension.GetStatValue(schoolDesk, VEFDefOf.VEF_BuildingLearningRateOffset, true, -1);
		return false;
	}
}
