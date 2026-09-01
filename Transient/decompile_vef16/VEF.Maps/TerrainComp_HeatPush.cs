using Verse;

namespace VEF.Maps;

public class TerrainComp_HeatPush : TerrainComp
{
	public TerrainCompProperties_HeatPush Props => (TerrainCompProperties_HeatPush)props;

	protected virtual bool ShouldPushHeat => true;

	protected virtual float PushAmount => Props.pushAmount;

	public override void CompTick()
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		base.CompTick();
		if (Find.TickManager.TicksGame % 60 == this.HashCodeToMod(60) && ShouldPushHeat)
		{
			GenTemperature.PushHeat(parent.Position, parent.Map, PushAmount);
		}
	}
}
