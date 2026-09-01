using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_HeatPusher : HediffComp
{
	public HediffCompProperties_HeatPusher Props => (HediffCompProperties_HeatPusher)(object)base.props;

	protected virtual bool ShouldPushHeatNow
	{
		get
		{
			if (!((Thing)((Hediff)base.parent).pawn).SpawnedOrAnyParentSpawned)
			{
				return false;
			}
			float ambientTemperature = ((Thing)((Hediff)base.parent).pawn).AmbientTemperature;
			if (ambientTemperature < Props.heatPushMaxTemperature)
			{
				return ambientTemperature > Props.heatPushMinTemperature;
			}
			return false;
		}
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, Props.tickCounter) && ShouldPushHeatNow)
		{
			GenTemperature.PushHeat(((Thing)((Hediff)base.parent).pawn).PositionHeld, ((Thing)((Hediff)base.parent).pawn).MapHeld, Props.heatPerSecond);
		}
	}
}
