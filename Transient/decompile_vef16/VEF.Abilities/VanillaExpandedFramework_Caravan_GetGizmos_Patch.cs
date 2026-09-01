using System.Collections.Generic;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

[HarmonyPatch(typeof(Caravan), "GetGizmos")]
public static class VanillaExpandedFramework_Caravan_GetGizmos_Patch
{
	[HarmonyPostfix]
	public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> gizmos, Caravan __instance)
	{
		foreach (Gizmo gizmo in gizmos)
		{
			yield return gizmo;
		}
		foreach (Pawn pawn in __instance.pawns)
		{
			CompAbilities compAbilities = ThingCompUtility.TryGetComp<CompAbilities>((Thing)(object)pawn);
			if (compAbilities == null)
			{
				continue;
			}
			foreach (Ability learnedAbility in compAbilities.LearnedAbilities)
			{
				if (learnedAbility.def.showGizmoOnWorldView && learnedAbility.ShowGizmoOnPawn())
				{
					yield return learnedAbility.GetGizmo();
				}
			}
		}
	}
}
