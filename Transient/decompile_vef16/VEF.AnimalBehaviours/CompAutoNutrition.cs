using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class CompAutoNutrition : ThingComp
{
	public CompProperties_AutoNutrition Props => (CompProperties_AutoNutrition)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (((Thing)base.parent).Map == null)
		{
			return;
		}
		Pawn_NeedsTracker needs = val.needs;
		if (needs != null)
		{
			Need_Food food = needs.food;
			if (((food != null) ? new float?(((Need)food).CurLevelPercentage) : ((float?)null)) < 0.5f && RestUtility.Awake(val))
			{
				Job val2 = JobMaker.MakeJob(DefDatabase<JobDef>.GetNamed("VEF_AutoNutrition", true), LocalTargetInfo.op_Implicit((Thing)(object)base.parent));
				val2.count = 1;
				val2.def.reportString = Props.consumingFoodReportString;
				val.jobs.TryTakeOrderedJob(val2, (JobTag?)(JobTag)0, false);
			}
		}
	}
}
