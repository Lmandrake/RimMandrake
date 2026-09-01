using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(FloatMenuOptionProvider_Ingest))]
[HarmonyPatch("GetSingleOptionFor")]
public static class VanillaExpandedFramework_FloatMenuOptionProvider_Ingest_GetSingleOptionFor_Patch
{
	[HarmonyPostfix]
	private static void RemoveErrorForNonForbiddables(FloatMenuContext context, Thing clickedThing, ref FloatMenuOption __result)
	{
		if (StaticCollectionsClass.draftable_animals.Contains((Thing)(object)context.FirstSelectedPawn) && ThingCompUtility.TryGetComp<CompForbiddable>(clickedThing) == null)
		{
			__result = null;
		}
	}
}
