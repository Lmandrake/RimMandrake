using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Abilities;

public class JobDriver_StandAndFaceTarget : JobDriver
{
	private CompAbilities cachedComp;

	public CompAbilities CompAbilities
	{
		get
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			if (cachedComp == null)
			{
				LocalTargetInfo targetA = ((JobDriver)this).TargetA;
				cachedComp = ((ThingWithComps)((LocalTargetInfo)(ref targetA)).Pawn).GetComp<CompAbilities>();
			}
			return cachedComp;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		return true;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOn<JobDriver_StandAndFaceTarget>(this, (Func<bool>)(() => CompAbilities.currentlyCasting == null));
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.tickAction = delegate
		{
			if (base.pawn.pather.Moving)
			{
				base.pawn.pather.StopDead();
			}
		};
		val.tickIntervalAction = delegate(int delta)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			if ((int)PawnUtility.GetPosture(base.pawn) == 0)
			{
				base.pawn.rotationTracker.FaceTarget(((JobDriver)this).TargetA);
			}
			PawnUtility.GainComfortFromCellIfPossible(base.pawn, delta, false);
		};
		val.socialMode = (RandomSocialMode)0;
		val.defaultCompleteMode = (ToilCompleteMode)5;
		val.handlingFacing = true;
		yield return val;
	}
}
