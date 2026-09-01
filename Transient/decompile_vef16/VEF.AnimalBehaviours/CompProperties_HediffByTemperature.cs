using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_HediffByTemperature : CompProperties
{
	public bool doTemperatureBelow;

	public bool doTemperatureAbove;

	public float temperatureBelow;

	public float temperatureAbove;

	public int tickInterval = 1000;

	public HediffDef hediffBelow;

	public HediffDef hediffAbove;

	public float severity = 1f;

	public BodyPartDef bodyPart;

	public CompProperties_HediffByTemperature()
	{
		base.compClass = typeof(CompHediffByTemperature);
	}
}
