using Verse;

namespace BigAndSmall;

public class CompProperties_TempGenerator : HediffCompProperties
{
	public float targetTemperature = 9999f;

	public float energyPerSecond = 21f;

	public bool scaleToBodySize = true;

	public CompProperties_TempGenerator()
	{
		base.compClass = typeof(TemperatureGenerator);
	}
}
