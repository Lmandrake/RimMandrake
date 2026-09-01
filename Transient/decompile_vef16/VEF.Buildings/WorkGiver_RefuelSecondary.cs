using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class WorkGiver_RefuelSecondary : WorkGiver_Scanner
{
	public override ThingRequest PotentialWorkThingRequest => ThingRequest.ForGroup((ThingRequestGroup)19);

	public override PathEndMode PathEndMode => (PathEndMode)2;

	public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		if (!CompProperties_Refuelable_DualFuel.allSecondaryFuelDefs.Contains(t.def))
		{
			return false;
		}
		CompRefuelable_DualFuel compRefuelable_DualFuel = ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(t);
		if (compRefuelable_DualFuel != null)
		{
			return CanRefuelSecondary(pawn, t, compRefuelable_DualFuel, forced);
		}
		return false;
	}

	public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
	{
		CompRefuelable_DualFuel compRefuelable_DualFuel = ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(t);
		if (compRefuelable_DualFuel != null)
		{
			return RefuelSecondaryJob(pawn, t, compRefuelable_DualFuel, forced);
		}
		return null;
	}

	private bool CanRefuelSecondary(Pawn pawn, Thing t, CompRefuelable_DualFuel compRefuelable, bool forced = false)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		if (compRefuelable == null || GridsUtility.Fogged((Thing)(object)((ThingComp)compRefuelable).parent) || compRefuelable.IsSecondaryFull)
		{
			return false;
		}
		if (!forced && !compRefuelable.allowAutoRefuelSecondary)
		{
			return false;
		}
		if (!forced && !compRefuelable.ShouldAutoRefuelSecondaryNow)
		{
			return false;
		}
		if (!ReservationUtility.CanReserve(pawn, LocalTargetInfo.op_Implicit(t), 1, -1, (ReservationLayerDef)null, forced))
		{
			return false;
		}
		if (t.Faction != ((Thing)pawn).Faction)
		{
			return false;
		}
		if (FindBestSecondaryFuel(pawn, t, compRefuelable) == null)
		{
			ThingFilter secondaryFuelFilter = compRefuelable.Props.secondaryFuelFilter;
			JobFailReason.Is(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("NoFuelToRefuel", NamedArgument.op_Implicit(secondaryFuelFilter.Summary))), (string)null);
			return false;
		}
		return true;
	}

	private Job RefuelSecondaryJob(Pawn pawn, Thing t, CompRefuelable_DualFuel compRefuelable, bool forced = false)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		Thing val = FindBestSecondaryFuel(pawn, t, compRefuelable);
		Job obj = JobMaker.MakeJob(InternalDefOf.VEF_RefuelSecondary, LocalTargetInfo.op_Implicit(t), LocalTargetInfo.op_Implicit(val));
		obj.count = compRefuelable.GetSecondaryFuelCountToFullyRefuel();
		return obj;
	}

	private Thing FindBestSecondaryFuel(Pawn pawn, Thing refuelable, CompRefuelable_DualFuel comp)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		ThingFilter filter = comp.Props.secondaryFuelFilter;
		return GenClosest.ClosestThingReachable(((Thing)pawn).Position, ((Thing)pawn).Map, filter.BestThingRequest, (PathEndMode)3, TraverseParms.For(pawn, (Danger)3, (TraverseMode)0, false, false, false, true), 9999f, (Predicate<Thing>)Validator, (IEnumerable<Thing>)null, 0, -1, false, (RegionType)14, false, false);
		bool Validator(Thing x)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			if (ForbidUtility.IsForbidden(x, pawn) || !ReservationUtility.CanReserve(pawn, LocalTargetInfo.op_Implicit(x), 1, -1, (ReservationLayerDef)null, false))
			{
				return false;
			}
			if (!filter.Allows(x))
			{
				return false;
			}
			return true;
		}
	}
}
