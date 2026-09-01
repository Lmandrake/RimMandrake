using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(CompAffectedByFacilities))]
[HarmonyPatch("CanPotentiallyLinkTo_Static")]
[HarmonyPatch(new Type[]
{
	typeof(ThingDef),
	typeof(IntVec3),
	typeof(Rot4),
	typeof(ThingDef),
	typeof(IntVec3),
	typeof(Rot4),
	typeof(Map)
})]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompAffectedByFacilities_CanPotentiallyLinkTo_Static_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (!(method != null))
		{
			return DefDatabase<ThingDef>.AllDefs.Any((ThingDef def) => ((Def)def).GetModExtension<FacilityExtension>()?.linkOnInteractionSpots ?? false);
		}
		return true;
	}

	private static bool Prefix(ThingDef facilityDef, IntVec3 facilityPos, Rot4 facilityRot, ThingDef myDef, IntVec3 myPos, Rot4 myRot, Map myMap, ref bool __result)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		FacilityExtension modExtension = ((Def)facilityDef).GetModExtension<FacilityExtension>();
		if (modExtension == null || !modExtension.linkOnInteractionSpots)
		{
			return true;
		}
		if (myDef.HasSingleOrMultipleInteractionCells)
		{
			List<IntVec3> list = ThingUtility.InteractionCellsWhenAt(myDef, myPos, myRot, myMap, true);
			CellRect rect = GenAdj.OccupiedRect(facilityPos, facilityRot, ((BuildableDef)facilityDef).Size);
			if (GenCollection.Any<IntVec3>(list, (Predicate<IntVec3>)((IntVec3 cell) => ((CellRect)(ref rect)).Contains(cell))))
			{
				__result = true;
				return true;
			}
		}
		__result = false;
		return false;
	}
}
