using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Pawn), "GetGizmos")]
public static class VanillaExpandedFramework_Pawn_GetGizmos_Lasers_Patch
{
	[HarmonyPostfix]
	public static void GetGizmos_PostFix(Pawn __instance, ref IEnumerable<Gizmo> __result)
	{
		Pawn_EquipmentTracker equipment = __instance.equipment;
		if (equipment == null)
		{
			return;
		}
		ThingWithComps primary = equipment.Primary;
		if (primary != null)
		{
			CompLaserCapacitor comp = primary.GetComp<CompLaserCapacitor>();
			if (comp != null && GizmoGetter(comp).Count() > 0 && __instance != null && ((Thing)__instance).Faction == Faction.OfPlayer)
			{
				__result = __result.Concat(GizmoGetter(comp));
			}
		}
	}

	public static IEnumerable<Gizmo> GizmoGetter(CompLaserCapacitor CompWargearWeapon)
	{
		IEnumerator<Gizmo> enumerator = ((ThingComp)CompWargearWeapon).CompGetGizmosExtra().GetEnumerator();
		while (enumerator.MoveNext())
		{
			yield return enumerator.Current;
		}
	}
}
