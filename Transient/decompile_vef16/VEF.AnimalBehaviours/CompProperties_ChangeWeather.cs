using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_ChangeWeather : CompProperties
{
	public int tickInterval = 250;

	public string weatherDef = "Fog";

	public bool isRandomWeathers;

	public List<WeatherDef> randomWeathers;

	public CompProperties_ChangeWeather()
	{
		base.compClass = typeof(CompChangeWeather);
	}
}
