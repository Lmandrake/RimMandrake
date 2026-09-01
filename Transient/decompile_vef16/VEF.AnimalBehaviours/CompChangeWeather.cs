using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompChangeWeather : ThingComp
{
	public CompProperties_ChangeWeather Props => (CompProperties_ChangeWeather)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (((Thing)base.parent).Map != null && Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			if (Props.isRandomWeathers)
			{
				((Thing)base.parent).Map.weatherManager.curWeather = GenCollection.RandomElement<WeatherDef>((IEnumerable<WeatherDef>)Props.randomWeathers);
				((Thing)base.parent).Map.weatherManager.TransitionTo(GenCollection.RandomElement<WeatherDef>((IEnumerable<WeatherDef>)Props.randomWeathers));
			}
			else if (((Thing)base.parent).Map.weatherManager.curWeather != WeatherDef.Named(Props.weatherDef))
			{
				((Thing)base.parent).Map.weatherManager.curWeather = WeatherDef.Named(Props.weatherDef);
				((Thing)base.parent).Map.weatherManager.TransitionTo(WeatherDef.Named(Props.weatherDef));
			}
		}
	}
}
