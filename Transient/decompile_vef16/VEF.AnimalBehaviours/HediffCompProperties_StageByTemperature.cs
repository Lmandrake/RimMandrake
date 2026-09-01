using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_StageByTemperature : HediffCompProperties
{
	public int minTemp;

	public int maxTemp;

	public HediffCompProperties_StageByTemperature()
	{
		base.compClass = typeof(HediffComp_StageByTemperature);
	}
}
