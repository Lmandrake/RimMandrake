using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class WorkGiver_DestroyItem : WorkGiver_Scanner
{
	public override PathEndMode PathEndMode => (PathEndMode)2;

	public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
	{
		return ((Thing)pawn).Map.GetComponent<DestroyableObjects_MapComponent>().objects_InMap;
	}

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		if (t == null || FireUtility.IsBurning(t) || !ThingCompUtility.TryGetComp<CompDestroyThisItem>(t).itemNeedsDestruction)
		{
			return false;
		}
		if (!ForbidUtility.IsForbidden(t, pawn))
		{
			LocalTargetInfo val = LocalTargetInfo.op_Implicit(t);
			if (ReservationUtility.CanReserve(pawn, val, 1, -1, (ReservationLayerDef)null, forced))
			{
				return true;
			}
		}
		return false;
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Expected O, but got Unknown
		return new Job(InternalDefOf.VEF_DestroyItem, LocalTargetInfo.op_Implicit(t));
	}
}
