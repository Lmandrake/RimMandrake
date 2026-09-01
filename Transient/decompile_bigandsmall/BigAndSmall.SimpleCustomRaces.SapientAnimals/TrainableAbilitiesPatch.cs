using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall.SimpleCustomRaces.SapientAnimals;

[HarmonyPatch(typeof(CompAbilityEffect_RequiresTrainable))]
internal static class TrainableAbilitiesPatch
{
	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPrefix]
	public static bool HasLearnedTrainable_Prefix(CompAbilityEffect_RequiresTrainable __instance, ref bool __result)
	{
		if (__instance != null)
		{
			Ability parent = ((AbilityComp)__instance).parent;
			bool? obj;
			if (parent == null)
			{
				obj = null;
			}
			else
			{
				Pawn pawn = parent.pawn;
				obj = ((pawn != null) ? new bool?(((Thing)pawn).def.race.Humanlike) : ((bool?)null));
			}
			bool? flag = obj;
			if (flag == true)
			{
				__result = true;
				return false;
			}
		}
		return true;
	}
}
