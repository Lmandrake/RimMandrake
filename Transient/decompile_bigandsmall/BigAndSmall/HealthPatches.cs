using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class HealthPatches
{
	[HarmonyPatch(typeof(MedicalRecipesUtility), "IsCleanAndDroppable")]
	public static class IsCleanAndDroppable_Patch
	{
		public static void Postfix(ref bool __result, Pawn pawn, BodyPartRecord part)
		{
			if (__result)
			{
				BSCache cache = HumanoidPawnScaler.GetCache(pawn);
				if (cache != null && !cache.partsCanBeHarvested)
				{
					__result = false;
				}
			}
		}
	}
}
