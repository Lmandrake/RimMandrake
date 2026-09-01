using System;
using System.Collections.Generic;
using System.Linq;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class JobDriver_RefuelSecondary : JobDriver
{
	private const TargetIndex RefuelableInd = 1;

	private const TargetIndex FuelInd = 2;

	public const int RefuelingDuration = 240;

	protected Thing Refuelable
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	protected CompRefuelable_DualFuel RefuelableComp => ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(Refuelable);

	protected Thing Fuel
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)2);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		if (ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Refuelable), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false))
		{
			return ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Fuel), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
		}
		return false;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_RefuelSecondary>(this, (TargetIndex)1);
		((JobDriver)this).AddEndCondition((Func<JobCondition>)(() => (!RefuelableComp.IsSecondaryFull) ? ((JobCondition)1) : ((JobCondition)2)));
		((JobDriver)this).AddFailCondition((Func<bool>)(() => !base.job.playerForced && !RefuelableComp.ShouldAutoRefuelSecondaryNowIgnoringFuelPct));
		((JobDriver)this).AddFailCondition((Func<bool>)(() => !RefuelableComp.allowAutoRefuelSecondary && !base.job.playerForced));
		yield return Toils_General.DoAtomic((Action)delegate
		{
			base.job.count = RefuelableComp.GetSecondaryFuelCountToFullyRefuel();
		});
		Toil reserveFuel = Toils_Reserve.Reserve((TargetIndex)2, 1, -1, (ReservationLayerDef)null, false);
		yield return reserveFuel;
		yield return ToilFailConditions.FailOnSomeonePhysicallyInteracting<Toil>(ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(Toils_Goto.GotoThing((TargetIndex)2, (PathEndMode)3, false), (TargetIndex)2), (TargetIndex)2);
		yield return ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(Toils_Haul.StartCarryThing((TargetIndex)2, false, true, false, true, false), (TargetIndex)2);
		yield return Toils_Haul.CheckForGetOpportunityDuplicate(reserveFuel, (TargetIndex)2, (TargetIndex)0, true, (Predicate<Thing>)null);
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		yield return ToilEffects.WithProgressBarToilDelay(ToilFailConditions.FailOnCannotTouch<Toil>(ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(Toils_General.Wait(240, (TargetIndex)0), (TargetIndex)2), (TargetIndex)1), (TargetIndex)1, (PathEndMode)2), (TargetIndex)1, false, -0.5f);
		yield return FinalizeSecondaryRefueling((TargetIndex)1, (TargetIndex)2);
	}

	public static Toil FinalizeSecondaryRefueling(TargetIndex refuelableInd, TargetIndex fuelInd)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		Toil toil = ToilMaker.MakeToil("FinalizeSecondaryRefueling");
		toil.initAction = delegate
		{
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			Job curJob = toil.actor.CurJob;
			LocalTargetInfo target = curJob.GetTarget(refuelableInd);
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			if (GenList.NullOrEmpty<ThingCountClass>((IList<ThingCountClass>)toil.actor.CurJob.placedThings))
			{
				CompRefuelable_DualFuel compRefuelable_DualFuel = ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(thing);
				List<Thing> list = new List<Thing>();
				target = curJob.GetTarget(fuelInd);
				list.Add(((LocalTargetInfo)(ref target)).Thing);
				compRefuelable_DualFuel.RefuelSecondary(list);
			}
			else
			{
				ThingCompUtility.TryGetComp<CompRefuelable_DualFuel>(thing).RefuelSecondary(toil.actor.CurJob.placedThings.Select((ThingCountClass p) => p.thing).ToList());
			}
		};
		toil.defaultCompleteMode = (ToilCompleteMode)1;
		return toil;
	}
}
