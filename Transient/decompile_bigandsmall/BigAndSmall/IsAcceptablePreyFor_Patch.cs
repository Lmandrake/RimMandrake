using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class IsAcceptablePreyFor_Patch
{
	public static void Postfix(ref bool __result, ref Pawn predator, Pawn prey)
	{
		if (prey != null && prey.needs != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(prey);
			if (cache != null && cache.animalFriend)
			{
				__result = false;
			}
		}
	}
}
