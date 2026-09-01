using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class CompTargetEffect_Reanimate : CompTargetEffect
{
	public static CompProperties_TargetEffectReanimate currentProps;

	public CompProperties_TargetEffectReanimate Props => (CompProperties_TargetEffectReanimate)(object)((ThingComp)this).props;

	public override void DoEffectOn(Pawn user, Thing target)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		JobDef val = DefDatabase<JobDef>.AllDefsListForReading.Find((JobDef x) => x.driverClass == typeof(JobDriver_Reanimate));
		if (val == null)
		{
			Log.Error("Could not find JobDriver_Resurrect");
		}
		else if (val != null && ReservationUtility.CanReserveAndReach(user, LocalTargetInfo.op_Implicit(target), (PathEndMode)2, (Danger)3, 1, -1, (ReservationLayerDef)null, false))
		{
			currentProps = Props;
			Job val2 = JobMaker.MakeJob(val, LocalTargetInfo.op_Implicit(target), LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)this).parent));
			val2.count = 1;
			user.jobs.TryTakeOrderedJob(val2, (JobTag?)(JobTag)0, false);
		}
	}
}
