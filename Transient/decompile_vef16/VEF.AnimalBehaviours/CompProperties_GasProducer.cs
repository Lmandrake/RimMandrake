using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_GasProducer : CompProperties
{
	public string gasType = "";

	public float rate;

	public int radius;

	public bool generateIfDowned;

	public CompProperties_GasProducer()
	{
		base.compClass = typeof(CompGasProducer);
	}
}
