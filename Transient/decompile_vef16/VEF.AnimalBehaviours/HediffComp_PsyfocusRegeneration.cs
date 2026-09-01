using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_PsyfocusRegeneration : HediffComp
{
	public HediffCompProperties_PsyfocusRegeneration Props => (HediffCompProperties_PsyfocusRegeneration)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.rateInTicks, delta))
		{
			Pawn pawn = ((Hediff)base.parent).pawn;
			if (pawn.psychicEntropy != null)
			{
				pawn.psychicEntropy.OffsetPsyfocusDirectly(Props.regenAmount);
			}
		}
	}
}
