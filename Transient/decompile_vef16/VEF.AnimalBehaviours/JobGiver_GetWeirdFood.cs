using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobGiver_GetWeirdFood : ThinkNode_JobGiver
{
	private HungerCategory minCategory;

	private float maxLevelPercentage = 1f;

	public bool forceScanWholeMap;

	private Effecter effecter;

	public override ThinkNode DeepCopy(bool resolve = true)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		JobGiver_GetWeirdFood obj = (JobGiver_GetWeirdFood)(object)((ThinkNode_JobGiver)this).DeepCopy(resolve);
		obj.minCategory = minCategory;
		obj.maxLevelPercentage = maxLevelPercentage;
		obj.forceScanWholeMap = forceScanWholeMap;
		return (ThinkNode)(object)obj;
	}

	public override float GetPriority(Pawn pawn)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Invalid comparison between Unknown and I4
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		Need_Food val = pawn?.needs?.food;
		if (val == null)
		{
			return 0f;
		}
		if ((int)pawn.needs.food.CurCategory < 3 && FoodUtility.ShouldBeFedBySomeone(pawn))
		{
			return 0f;
		}
		if (val.CurCategory < minCategory)
		{
			return 0f;
		}
		if (((Need)val).CurLevelPercentage > maxLevelPercentage)
		{
			return 0f;
		}
		if (((Need)val).CurLevelPercentage < pawn.RaceProps.FoodLevelPercentageWantEat)
		{
			return 9.5f;
		}
		return 0f;
	}

	protected override Job TryGiveJob(Pawn pawn)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_019d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		Need_Food val = pawn?.needs?.food;
		if (val == null || val.CurCategory < minCategory || ((Need)val).CurLevelPercentage > maxLevelPercentage)
		{
			return null;
		}
		ThingDef val2 = null;
		Thing val3 = null;
		CompEatWeirdFood compEatWeirdFood = ThingCompUtility.TryGetComp<CompEatWeirdFood>((Thing)(object)pawn);
		if (compEatWeirdFood != null)
		{
			foreach (string item in compEatWeirdFood.Props.customThingToEat)
			{
				val2 = DefDatabase<ThingDef>.GetNamedSilentFail(item);
				if (val2 != null)
				{
					val3 = FindWeirdFoodInMap(val2, pawn);
					if (val3 != null)
					{
						break;
					}
				}
			}
			if (val3 != null && ((Thing)pawn).Map.reservationManager.CanReserve(pawn, LocalTargetInfo.op_Implicit(val3), 1, -1, (ReservationLayerDef)null, false))
			{
				Job obj = JobMaker.MakeJob(InternalDefOf.VEF_IngestWeird, LocalTargetInfo.op_Implicit(val3));
				obj.count = 1;
				return obj;
			}
			if (((Thing)pawn).Map != null && compEatWeirdFood.Props.digThingIfMapEmpty)
			{
				Pawn_NeedsTracker needs = pawn.needs;
				float? obj2;
				if (needs == null)
				{
					obj2 = null;
				}
				else
				{
					Need_Food food = needs.food;
					obj2 = ((food != null) ? new float?(((Need)food).CurLevelPercentage) : ((float?)null));
				}
				float? num = obj2;
				Pawn_NeedsTracker needs2 = pawn.needs;
				float? obj3;
				if (needs2 == null)
				{
					obj3 = null;
				}
				else
				{
					Need_Food food2 = needs2.food;
					obj3 = ((food2 != null) ? new float?(food2.PercentageThreshHungry) : ((float?)null));
				}
				if (num < obj3 && RestUtility.Awake(pawn))
				{
					ThingDef val4 = ThingDef.Named(compEatWeirdFood.Props.thingToDigIfMapEmpty);
					Thing val5 = null;
					for (int i = 0; i < compEatWeirdFood.Props.customAmountToDig; i++)
					{
						val5 = GenSpawn.Spawn(val4, ((Thing)pawn).Position, ((Thing)pawn).Map, (WipeMode)0);
					}
					if (effecter == null)
					{
						effecter = EffecterDefOf.Mine.Spawn();
					}
					effecter.Trigger(TargetInfo.op_Implicit((Thing)(object)pawn), TargetInfo.op_Implicit(val5), -1);
				}
			}
			return null;
		}
		return null;
	}

	public Thing FindWeirdFoodInMap(ThingDef thingDef, Pawn pawn)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		ThingRequest val = ThingRequest.ForDef(thingDef);
		bool flag = ForbidUtility.CaresAboutForbidden(pawn, true, false) && pawn.playerSettings != null && pawn.playerSettings.EffectiveAreaRestrictionInPawnCurrentMap != null;
		Thing val2 = GenClosest.ClosestThingReachable(((Thing)pawn).Position, ((Thing)pawn).Map, val, (PathEndMode)3, TraverseParms.For(pawn, (Danger)3, (TraverseMode)0, false, false, false, true), 9999f, (Predicate<Thing>)null, (IEnumerable<Thing>)null, 0, -1, false, (RegionType)14, flag, false);
		if (val2 != null && ForbidUtility.InAllowedArea(val2.Position, pawn))
		{
			return val2;
		}
		return null;
	}
}
