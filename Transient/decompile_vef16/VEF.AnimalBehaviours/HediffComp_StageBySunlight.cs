using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_StageBySunlight : HediffComp
{
	public HediffCompProperties_StageBySunlight Props => (HediffCompProperties_StageBySunlight)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, 500, delta))
		{
			if (((Thing)((Hediff)base.parent).pawn).Map != null && SanguophageUtility.InSunlight(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map))
			{
				((Hediff)base.parent).Severity = Props.sunlightStageIndex;
			}
			else
			{
				((Hediff)base.parent).Severity = Props.sunlessStageIndex;
			}
		}
	}
}
