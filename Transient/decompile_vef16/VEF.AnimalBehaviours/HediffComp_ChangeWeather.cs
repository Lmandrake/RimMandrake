using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_ChangeWeather : HediffComp
{
	public HediffCompProperties_ChangeWeather Props => (HediffCompProperties_ChangeWeather)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (((Thing)((Hediff)base.parent).pawn).Map != null && Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, Props.tickInterval, delta))
		{
			if (Props.isRandomWeathers)
			{
				((Thing)((Hediff)base.parent).pawn).Map.weatherManager.curWeather = GenCollection.RandomElement<WeatherDef>((IEnumerable<WeatherDef>)Props.randomWeathers);
				((Thing)((Hediff)base.parent).pawn).Map.weatherManager.TransitionTo(GenCollection.RandomElement<WeatherDef>((IEnumerable<WeatherDef>)Props.randomWeathers));
			}
			else if (((Thing)((Hediff)base.parent).pawn).Map.weatherManager.curWeather != WeatherDef.Named(Props.weatherDef))
			{
				((Thing)((Hediff)base.parent).pawn).Map.weatherManager.curWeather = WeatherDef.Named(Props.weatherDef);
				((Thing)((Hediff)base.parent).pawn).Map.weatherManager.TransitionTo(WeatherDef.Named(Props.weatherDef));
			}
		}
	}
}
