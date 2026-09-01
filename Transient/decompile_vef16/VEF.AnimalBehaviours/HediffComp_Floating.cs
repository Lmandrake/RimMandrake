using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Floating : HediffComp
{
	public HediffCompProperties_Floating Props => (HediffCompProperties_Floating)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.checkingInterval, delta))
		{
			StaticCollectionsClass.AddFloatingAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
		}
	}

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		StaticCollectionsClass.AddFloatingAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void CompPostPostRemoved()
	{
		StaticCollectionsClass.RemoveFloatingAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		StaticCollectionsClass.RemoveFloatingAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void Notify_PawnKilled()
	{
		StaticCollectionsClass.RemoveFloatingAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
	}
}
