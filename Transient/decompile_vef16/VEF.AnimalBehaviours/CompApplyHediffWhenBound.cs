using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class CompApplyHediffWhenBound : ThingComp
{
	public Pawn bondedPawn;

	public bool leavingMap;

	public CompProperties_ApplyHediffWhenBound Props => (CompProperties_ApplyHediffWhenBound)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Pawn>(ref bondedPawn, "bondedPawn", false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkingInterval, delta) || ((Thing)base.parent).Map == null)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		bool flag = false;
		foreach (Pawn allMapsCaravansAndTravellingTransporters_Alive_FreeColonist in PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_FreeColonists)
		{
			if (allMapsCaravansAndTravellingTransporters_Alive_FreeColonist.relations.DirectRelationExists(PawnRelationDefOf.Bond, val))
			{
				bondedPawn = allMapsCaravansAndTravellingTransporters_Alive_FreeColonist;
				flag = true;
			}
		}
		if (flag)
		{
			val.health.AddHediff(Props.hediffToApply, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			if (Props.applyHediffToBonded)
			{
				bondedPawn.health.AddHediff(Props.hediffToApplyToBonded, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			return;
		}
		Hediff firstHediffOfDef = val.health.hediffSet.GetFirstHediffOfDef(Props.hediffToApply, false);
		if (firstHediffOfDef != null)
		{
			val.health.RemoveHediff(firstHediffOfDef);
		}
		IntVec3 val2 = default(IntVec3);
		if (Props.doJobIfBondedDies && bondedPawn != null && bondedPawn.Dead && !leavingMap && RCellFinder.TryFindRandomExitSpot(val, ref val2, (TraverseMode)1))
		{
			val.MentalState.RecoverFromState();
			((Thing)val).SetFaction((Faction)null, (Pawn)null);
			Job val3 = JobMaker.MakeJob(Props.jobToDoIfBondedDies, LocalTargetInfo.op_Implicit(val2));
			val3.exitMapOnArrival = true;
			val.jobs.TryTakeOrderedJob(val3, (JobTag?)(JobTag)0, false);
			leavingMap = true;
		}
		if (Props.dieIfBondedDies && bondedPawn != null && bondedPawn.Dead)
		{
			((Thing)base.parent).Kill((DamageInfo?)null, (Hediff)null);
		}
	}
}
