using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(PawnUtility))]
[HarmonyPatch("IsFighting")]
public static class VanillaExpandedFramework_PawnUtility_IsFighting_Patch
{
	[HarmonyPostfix]
	public static void DontFlee(Pawn pawn, ref bool __result)
	{
		if (pawn != null && StaticCollectionsClass.nofleeing_animals.Contains((Thing)(object)pawn) && pawn.CurJob != null)
		{
			__result = true;
		}
	}
}
