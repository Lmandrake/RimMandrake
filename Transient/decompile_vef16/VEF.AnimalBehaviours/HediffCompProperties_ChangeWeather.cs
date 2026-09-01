using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_ChangeWeather : HediffCompProperties
{
	public int tickInterval = 250;

	public string weatherDef = "Fog";

	public bool isRandomWeathers;

	public List<WeatherDef> randomWeathers;

	public HediffCompProperties_ChangeWeather()
	{
		base.compClass = typeof(HediffComp_ChangeWeather);
	}
}
