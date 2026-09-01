using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_StageByHealth : HediffComp
{
	public HediffCompProperties_StageByHealth Props => (HediffCompProperties_StageByHealth)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, 500, delta))
		{
			if (((Thing)((Hediff)base.parent).pawn).Map != null && ((Hediff)base.parent).pawn.health.summaryHealth.SummaryHealthPercent >= Props.healthThreshold)
			{
				((Hediff)base.parent).Severity = Props.highHealthStageIndex;
			}
			else
			{
				((Hediff)base.parent).Severity = Props.lowHealthStageIndex;
			}
		}
	}
}
