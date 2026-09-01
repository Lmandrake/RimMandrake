using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(FloatMenuOptionProvider_WorkGivers))]
[HarmonyPatch("GetWorkGiverOption")]
public static class VanillaExpandedFramework_FloatMenuOptionProvider_WorkGivers_GetWorkGiverOption_Patch
{
	[HarmonyPostfix]
	private static void NoWorkBesidesAttacks(Pawn pawn, ref FloatMenuOption __result)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)pawn))
		{
			__result = null;
		}
	}
}
