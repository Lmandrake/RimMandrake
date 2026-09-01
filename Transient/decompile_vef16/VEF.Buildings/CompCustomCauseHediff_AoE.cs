using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompCustomCauseHediff_AoE : ThingComp
{
	protected static Room tempWorkingRoom;

	protected CompPowerTrader powerTrader;

	protected CompProperties_CustomCauseHediff_AoE Props => (CompProperties_CustomCauseHediff_AoE)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		powerTrader = base.parent.GetComp<CompPowerTrader>();
	}

	public override void CompTickInterval(int delta)
	{
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkInterval, delta))
		{
			TickInterval(Props.checkInterval);
		}
	}

	public override void CompTickRare()
	{
		TickInterval(250);
	}

	public override void CompTickLong()
	{
		TickInterval(2000);
	}

	protected virtual void TickInterval(int delta)
	{
		CompPowerTrader val = powerTrader;
		if (val == null || !val.PowerOn || !((Thing)base.parent).SpawnedOrAnyParentSpawned)
		{
			return;
		}
		try
		{
			bool worksInside = Props.worksInside;
			bool worksOutside = Props.worksOutside;
			if (!worksInside)
			{
				if (!worksOutside)
				{
					return;
				}
				tempWorkingRoom = RegionAndRoomQuery.GetRoom((Thing)(object)base.parent, (RegionType)15);
				Room val2 = tempWorkingRoom;
				if (val2 != null && !val2.PsychologicallyOutdoors)
				{
					return;
				}
			}
			else if (!worksOutside)
			{
				tempWorkingRoom = RegionAndRoomQuery.GetRoom((Thing)(object)base.parent, (RegionType)15);
				if (tempWorkingRoom == null || tempWorkingRoom.PsychologicallyOutdoors)
				{
					return;
				}
			}
			IReadOnlyList<Pawn> allPawnsSpawned = ((Thing)base.parent).MapHeld.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < allPawnsSpawned.Count; i++)
			{
				Pawn val3 = allPawnsSpawned[i];
				if (IsPawnAffectedAndInRange(val3, cacheRoom: true))
				{
					GiveOrUpdateHediff(val3);
				}
				Thing carriedThing = val3.carryTracker.CarriedThing;
				Pawn val4 = (Pawn)(object)((carriedThing is Pawn) ? carriedThing : null);
				if (val4 != null && IsPawnAffectedAndInRange(val4, cacheRoom: true))
				{
					GiveOrUpdateHediff(val4);
				}
			}
		}
		finally
		{
			tempWorkingRoom = null;
		}
	}

	protected virtual Hediff GiveOrUpdateHediff(Pawn target)
	{
		Hediff val = target.health.hediffSet.GetFirstHediffOfDef(Props.hediff, false);
		if (val == null)
		{
			val = target.health.AddHediff(Props.hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			val.Severity = Props.startingSeverity;
		}
		if (Props.hediffDuration > 0)
		{
			HediffWithComps val2 = (HediffWithComps)(object)((val is HediffWithComps) ? val : null);
			if (val2 != null)
			{
				HediffComp_Disappears comp = val2.GetComp<HediffComp_Disappears>();
				if (comp == null)
				{
					Log.ErrorOnce(((Def)((Thing)base.parent).def).defName + " has CompCustomCauseHediff_AoE with positive hediffDuration and has a hediff in props which does not have a HediffComp_Disappears", Gen.HashCombineInt(808055567, (int)((Def)val.def).shortHash));
				}
				else
				{
					comp.ticksToDisappear = Props.hediffDuration;
				}
			}
			else
			{
				Log.ErrorOnce(((Def)((Thing)base.parent).def).defName + " has CompCustomCauseHediff_AoE with positive hediffDuration and has a hediff which is not HediffWithComps", Gen.HashCombineInt(-837742526, (int)((Def)val.def).shortHash));
			}
		}
		return val;
	}

	public bool IsPawnAffectedAndInRange(Pawn pawn)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		if (IsPawnAffected(pawn))
		{
			return IsPositionInRange(((Thing)pawn).PositionHeld, cacheRoom: false);
		}
		return false;
	}

	protected bool IsPawnAffectedAndInRange(Pawn pawn, bool cacheRoom)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		if (IsPawnAffected(pawn))
		{
			return IsPositionInRange(((Thing)pawn).PositionHeld, cacheRoom);
		}
		return false;
	}

	public virtual bool IsPawnAffected(Pawn target)
	{
		if (target.health == null || target.Dead)
		{
			return false;
		}
		if (!IsAllowedPawnType(target))
		{
			return false;
		}
		if (Props.mustBeAwake && !RestUtility.Awake(target))
		{
			return false;
		}
		List<PawnCapacityDef> requiredCapacities = Props.requiredCapacities;
		if (requiredCapacities != null)
		{
			for (int i = 0; i < requiredCapacities.Count; i++)
			{
				PawnCapacityDef val = requiredCapacities[i];
				if (!target.health.capacities.CapableOf(val))
				{
					return false;
				}
			}
		}
		return true;
	}

	public bool IsPositionInRange(IntVec3 position)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return IsPositionInRange(position, cacheRoom: false);
	}

	protected virtual bool IsPositionInRange(IntVec3 position, bool cacheRoom)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		CompProperties_CustomCauseHediff_AoE props = Props;
		if (props.range > 0f && (float)IntVec3Utility.DistanceToSquared(position, ((Thing)base.parent).PositionHeld) > props.range * props.range)
		{
			return false;
		}
		if (!props.sameRoomOnly)
		{
			return true;
		}
		if (cacheRoom)
		{
			return GridsUtility.GetRoom(position, ((Thing)base.parent).MapHeld) == (tempWorkingRoom ?? (tempWorkingRoom = RegionAndRoomQuery.GetRoom((Thing)(object)base.parent, (RegionType)15)));
		}
		return GridsUtility.GetRoom(position, ((Thing)base.parent).MapHeld) == (tempWorkingRoom ?? RegionAndRoomQuery.GetRoom((Thing)(object)base.parent, (RegionType)15));
	}

	protected virtual bool IsAllowedPawnType(Pawn target)
	{
		RaceProperties raceProps = target.RaceProps;
		if (raceProps.Humanlike)
		{
			return Props.allowHumanlike;
		}
		if (raceProps.Dryad)
		{
			return Props.allowDryads;
		}
		if (raceProps.Insect)
		{
			return Props.allowInsects;
		}
		if (raceProps.Animal)
		{
			return Props.allowAnimals;
		}
		if (raceProps.IsMechanoid)
		{
			return Props.allowMechanoids;
		}
		if (raceProps.IsAnomalyEntity)
		{
			return Props.allowEntities;
		}
		return false;
	}
}
