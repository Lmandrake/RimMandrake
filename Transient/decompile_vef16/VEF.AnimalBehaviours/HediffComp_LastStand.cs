using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_LastStand : HediffComp
{
	public int tickCounter;

	public HediffCompProperties_LastStand Props => (HediffCompProperties_LastStand)(object)base.props;

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		StaticCollectionsClass.AddLastStandAnimalToList((Thing)(object)((Hediff)base.parent).pawn, Props.finalCoolDownMultiplier);
	}

	public override void CompPostPostRemoved()
	{
		StaticCollectionsClass.RemoveLastStandAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		StaticCollectionsClass.RemoveLastStandAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void Notify_PawnKilled()
	{
		StaticCollectionsClass.RemoveLastStandAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
	}
}
