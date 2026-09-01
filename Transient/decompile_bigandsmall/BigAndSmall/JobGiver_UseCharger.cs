using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class JobGiver_UseCharger : ThinkNode_JobGiver
{
	private const float maxLevelPercentage = 1f;

	public override float GetPriority(Pawn pawn)
	{
		Need_Food food = pawn.needs.food;
		if (food == null)
		{
			return 0f;
		}
		if (((Need)food).CurLevelPercentage >= pawn.RaceProps.FoodLevelPercentageWantEat)
		{
			return 0f;
		}
		BSCache cachePrepatched = pawn.GetCachePrepatched();
		if (cachePrepatched != null && cachePrepatched.canUseChargers)
		{
			if (cachePrepatched.poorUserOfChargers)
			{
				return 9.45f;
			}
			return 9.55f;
		}
		return 0f;
	}

	protected override Job TryGiveJob(Pawn pawn)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Expected I4, but got Unknown
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		Need_Food food = pawn.needs.food;
		if (food == null || ((Need)food).CurLevelPercentage > 1f)
		{
			return null;
		}
		HungerCategory curCategory = food.CurCategory;
		Thing val = GenClosest.ClosestThingReachable(((Thing)pawn).Position, ((Thing)pawn).Map, ThingRequest.ForGroup((ThingRequestGroup)10), (PathEndMode)2, TraverseParms.For(pawn, (Danger)3, (TraverseMode)0, false, false, false, true), (curCategory - 1) switch
		{
			0 => 24f, 
			1 => 48f, 
			2 => 99999f, 
			_ => 0f, 
		}, (Predicate<Thing>)predicate, (IEnumerable<Thing>)null, 0, -1, false, (RegionType)14, false, false);
		if (val != null)
		{
			return JobMaker.MakeJob(BSDefs.BS_UseCharger, LocalTargetInfo.op_Implicit(val));
		}
		return null;
		bool predicate(Thing t)
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			if (t is IRobotCharger robotCharger && ReservationUtility.CanReserve(pawn, LocalTargetInfo.op_Implicit(t), 1, -1, (ReservationLayerDef)null, false))
			{
				return robotCharger.PawnCanUse(pawn, isNew: true);
			}
			return false;
		}
	}
}
