using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_StageByPsylink : HediffComp
{
	public HediffCompProperties_StageByPsylink Props => (HediffCompProperties_StageByPsylink)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, 500, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null && ModsConfig.RoyaltyActive)
		{
			float num = (float)PawnUtility.GetPsylinkLevel(((Hediff)base.parent).pawn) / 6f;
			if (num == 0f)
			{
				num = 0.01f;
			}
			((Hediff)base.parent).Severity = num;
		}
	}
}
