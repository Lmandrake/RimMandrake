using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_GasProducer : HediffComp
{
	public HediffCompProperties_GasProducer Props => (HediffCompProperties_GasProducer)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, Props.timer, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null)
		{
			GasUtility.AddGas(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, Props.gasType, Props.amount);
		}
	}
}
