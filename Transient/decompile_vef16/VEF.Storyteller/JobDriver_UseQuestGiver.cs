using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace VEF.Storyteller;

public class JobDriver_UseQuestGiver : JobDriver
{
	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		return ReservationUtility.Reserve(base.pawn, base.job.targetA, base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDespawnedOrNull<JobDriver_UseQuestGiver>(this, (TargetIndex)1);
		yield return Toils_Goto.GotoCell((TargetIndex)1, (PathEndMode)4);
		Toil openComms = ToilMaker.MakeToil("MakeNewToils");
		openComms.initAction = delegate
		{
			ThingCompUtility.TryGetComp<CompQuestGiver>(((LocalTargetInfo)(ref openComms.actor.CurJob.targetA)).Thing).Use();
		};
		yield return openComms;
	}
}
