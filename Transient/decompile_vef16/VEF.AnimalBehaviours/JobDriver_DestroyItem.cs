using System.Collections.Generic;
using System.Diagnostics;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobDriver_DestroyItem : JobDriver
{
	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = base.pawn;
		LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
		return ReservationUtility.Reserve(pawn, LocalTargetInfo.op_Implicit(((LocalTargetInfo)(ref target)).Thing), base.job, 1, -1, (ReservationLayerDef)null, true, false);
	}

	[DebuggerHidden]
	protected override IEnumerable<Toil> MakeNewToils()
	{
		LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
		Thing itemToDestroy = ((LocalTargetInfo)(ref target)).Thing;
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_DestroyItem>(this, (TargetIndex)1);
		ToilFailConditions.FailOnBurningImmobile<JobDriver_DestroyItem>(this, (TargetIndex)1);
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		yield return ToilEffects.WithProgressBarToilDelay(ToilFailConditions.FailOnCannotTouch<Toil>(ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(Toils_General.Wait(1200, (TargetIndex)0), (TargetIndex)1), (TargetIndex)1, (PathEndMode)2), (TargetIndex)1, false, -0.5f);
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.initAction = delegate
		{
			((Entity)itemToDestroy).DeSpawn((DestroyMode)0);
		};
		val.defaultCompleteMode = (ToilCompleteMode)1;
		yield return val;
	}
}
