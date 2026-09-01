using System;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Polluter : HediffComp
{
	public HediffCompProperties_Polluter Props => (HediffCompProperties_Polluter)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, Props.timer, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null)
		{
			PollutionUtility.GrowPollutionAt(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, Props.amount, (Action<IntVec3>)null, true, (Func<IntVec3, bool>)null);
		}
	}
}
