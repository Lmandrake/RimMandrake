using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_RemoveFromMechs : HediffComp
{
	public HediffCompProperties_RemoveFromMechs Props => (HediffCompProperties_RemoveFromMechs)(object)base.props;

	public override void CompPostMake()
	{
		((HediffComp)this).CompPostMake();
		if (((Hediff)base.parent).pawn.RaceProps.IsMechanoid)
		{
			((Hediff)base.parent).pawn.health.RemoveHediff((Hediff)(object)base.parent);
		}
	}
}
