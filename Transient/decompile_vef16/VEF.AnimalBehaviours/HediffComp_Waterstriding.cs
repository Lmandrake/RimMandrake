using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Waterstriding : HediffComp
{
	public HediffCompProperties_Waterstriding Props => (HediffCompProperties_Waterstriding)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.checkingInterval, delta))
		{
			StaticCollectionsClass.AddWaterstridingPawnToList((Thing)(object)((Hediff)base.parent).pawn);
		}
	}

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		StaticCollectionsClass.AddWaterstridingPawnToList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void CompPostPostRemoved()
	{
		StaticCollectionsClass.RemoveWaterstridingPawnFromList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		StaticCollectionsClass.RemoveWaterstridingPawnFromList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void Notify_PawnKilled()
	{
		StaticCollectionsClass.RemoveWaterstridingPawnFromList((Thing)(object)((Hediff)base.parent).pawn);
	}
}
