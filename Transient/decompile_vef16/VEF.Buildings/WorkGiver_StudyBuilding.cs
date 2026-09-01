using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class WorkGiver_StudyBuilding : WorkGiver_Scanner
{
	public override PathEndMode PathEndMode => (PathEndMode)2;

	public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
	{
		return ((Thing)pawn).Map.GetComponent<MapComponent_InteractableBuildingsInMap>().studiables_InMap;
	}

	public override bool ShouldSkip(Pawn pawn, bool forced = false)
	{
		return ((Thing)pawn).Map.GetComponent<MapComponent_InteractableBuildingsInMap>().studiables_InMap.Count == 0;
	}

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		if (!(t is StudiableBuilding studiableBuilding))
		{
			return false;
		}
		if (t.Faction != ((Thing)pawn).Faction)
		{
			return false;
		}
		if (ForbidUtility.IsForbidden(t, pawn))
		{
			return false;
		}
		if (!ReservationUtility.CanReserve(pawn, LocalTargetInfo.op_Implicit((Thing)(object)studiableBuilding), 1, -1, (ReservationLayerDef)null, forced))
		{
			return false;
		}
		if (((Thing)pawn).Map.designationManager.DesignationOn((Thing)(object)studiableBuilding, DesignationDefOf.Deconstruct) != null)
		{
			return false;
		}
		if (FireUtility.IsBurning((Thing)(object)studiableBuilding))
		{
			return false;
		}
		return true;
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Expected O, but got Unknown
		return new Job(InternalDefOf.VFE_StudyBuilding, LocalTargetInfo.op_Implicit(t));
	}
}
