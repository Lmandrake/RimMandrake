using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Pawn))]
[HarmonyPatch("WorkTypeIsDisabled")]
public static class VanillaExpandedFramework_Pawn_WorkTypeIsDisabled_Patch
{
	[HarmonyPostfix]
	private static void RemoveTendFromAnimals(WorkTypeDef w, Pawn __instance, ref bool __result)
	{
		if (w == WorkTypeDefOf.Doctor && StaticCollectionsClass.draftable_animals.Contains((Thing)(object)__instance) && !__instance.RaceProps.IsMechanoid)
		{
			__result = true;
		}
	}
}
