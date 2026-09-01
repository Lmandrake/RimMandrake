using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class WorkGiver_AnimalResource : WorkGiver_GatherAnimalBodyResources
{
	protected override JobDef JobDef => InternalDefOf.VEF_AnimalResource;

	protected override CompHasGatherableBodyResource GetComp(Pawn animal)
	{
		return (CompHasGatherableBodyResource)(object)ThingCompUtility.TryGetComp<CompAnimalProduct>((Thing)(object)animal);
	}

	public override bool ShouldSkip(Pawn pawn, bool forced = false)
	{
		List<Pawn> list = ((Thing)pawn).Map.mapPawns.SpawnedPawnsInFaction(((Thing)pawn).Faction);
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i].RaceProps.Animal || list[i].RaceProps.IsMechanoid)
			{
				CompHasGatherableBodyResource comp = ((WorkGiver_GatherAnimalBodyResources)this).GetComp(list[i]);
				if (comp != null && comp.ActiveAndFull)
				{
					return false;
				}
			}
		}
		return true;
	}

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((t is Pawn) ? t : null);
		if (pawn.RaceProps.IsMechanoid)
		{
			return false;
		}
		if (val == null || (!val.RaceProps.Animal && !val.RaceProps.IsMechanoid))
		{
			return false;
		}
		CompHasGatherableBodyResource comp = ((WorkGiver_GatherAnimalBodyResources)this).GetComp(val);
		if (comp == null || !comp.ActiveAndFull || val.Downed || (val.roping != null && val.roping.IsRopedByPawn) || !PawnUtility.CanCasuallyInteractNow(val, false, false, false, false) || !ReservationUtility.CanReserve(pawn, LocalTargetInfo.op_Implicit((Thing)(object)val), 1, -1, (ReservationLayerDef)null, forced))
		{
			return false;
		}
		return true;
	}
}
