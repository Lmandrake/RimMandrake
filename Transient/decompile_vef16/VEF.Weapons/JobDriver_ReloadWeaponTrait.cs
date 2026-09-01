using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

public class JobDriver_ReloadWeaponTrait : JobDriver
{
	private const TargetIndex GearInd = 1;

	private const TargetIndex AmmoInd = 2;

	private Thing Gear
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		ReservationUtility.ReserveAsManyAsPossible(base.pawn, base.job.GetTargetQueue((TargetIndex)2), base.job, 1, -1, (ReservationLayerDef)null);
		return true;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		Thing gear = Gear;
		CompApplyWeaponTraits reloadableComp = ((gear != null) ? ThingCompUtility.TryGetComp<CompApplyWeaponTraits>(gear) : null);
		ToilFailConditions.FailOn<JobDriver_ReloadWeaponTrait>(this, (Func<bool>)(() => reloadableComp == null));
		ToilFailConditions.FailOn<JobDriver_ReloadWeaponTrait>(this, (Func<bool>)(() => !reloadableComp.NeedsReload()));
		ToilFailConditions.FailOnDestroyedOrNull<JobDriver_ReloadWeaponTrait>(this, (TargetIndex)1);
		ToilFailConditions.FailOnIncapable<JobDriver_ReloadWeaponTrait>(this, PawnCapacityDefOf.Manipulation);
		Toil getNextIngredient = Toils_General.Label();
		yield return getNextIngredient;
		foreach (Toil item in ReloadAsMuchAsPossible(reloadableComp))
		{
			yield return item;
		}
		yield return Toils_JobTransforms.ExtractNextTargetFromQueue((TargetIndex)2, true);
		yield return ToilFailConditions.FailOnSomeonePhysicallyInteracting<Toil>(ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(Toils_Goto.GotoThing((TargetIndex)2, (PathEndMode)3, false), (TargetIndex)2), (TargetIndex)2);
		yield return ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(Toils_Haul.StartCarryThing((TargetIndex)2, false, true, false, true, false), (TargetIndex)2);
		yield return Toils_Jump.JumpIf(getNextIngredient, (Func<bool>)(() => !GenList.NullOrEmpty<LocalTargetInfo>((IList<LocalTargetInfo>)base.job.GetTargetQueue((TargetIndex)2))));
		foreach (Toil item2 in ReloadAsMuchAsPossible(reloadableComp))
		{
			yield return item2;
		}
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.initAction = delegate
		{
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			Thing carriedThing = base.pawn.carryTracker.CarriedThing;
			if (carriedThing != null && !carriedThing.Destroyed)
			{
				Thing val2 = default(Thing);
				base.pawn.carryTracker.TryDropCarriedThing(((Thing)base.pawn).Position, (ThingPlaceMode)1, ref val2, (Action<Thing, int>)null);
			}
		};
		val.defaultCompleteMode = (ToilCompleteMode)1;
		yield return val;
	}

	private IEnumerable<Toil> ReloadAsMuchAsPossible(CompApplyWeaponTraits reloadable)
	{
		Toil done = Toils_General.Label();
		yield return Toils_Jump.JumpIf(done, (Func<bool>)(() => base.pawn.carryTracker.CarriedThing == null || base.pawn.carryTracker.CarriedThing.stackCount < reloadable.MinAmmoNeeded()));
		yield return ToilEffects.WithProgressBarToilDelay(Toils_General.Wait(reloadable.AbilityDetailsForWeapon(reloadable.GetDetails()).baseReloadTicks, (TargetIndex)0), (TargetIndex)1, false, -0.5f);
		Toil val = ToilMaker.MakeToil("ReloadAsMuchAsPossible");
		val.initAction = delegate
		{
			Thing carriedThing = base.pawn.carryTracker.CarriedThing;
			reloadable.ReloadFrom(base.pawn, carriedThing);
		};
		val.defaultCompleteMode = (ToilCompleteMode)1;
		yield return val;
		yield return done;
	}
}
