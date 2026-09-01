using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_StageByTemperature : HediffComp
{
	public HediffCompProperties_StageByTemperature Props => (HediffCompProperties_StageByTemperature)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, 500, delta) && ((Thing)((Hediff)base.parent).pawn).Map != null)
		{
			float severity = Mathf.Clamp((GridsUtility.GetTemperature(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map) - (float)Props.minTemp) / (float)(Props.maxTemp - Props.minTemp), 0f, 1f);
			((Hediff)base.parent).Severity = severity;
		}
	}
}
