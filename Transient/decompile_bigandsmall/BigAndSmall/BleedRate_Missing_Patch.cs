using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public class BleedRate_Missing_Patch
{
	public static void Postfix(ref float __result, ref Pawn_HealthTracker __instance, ref Pawn ___pawn)
	{
		__result = BleedRatePatch.SetBleedRate(__result, ___pawn);
	}
}
