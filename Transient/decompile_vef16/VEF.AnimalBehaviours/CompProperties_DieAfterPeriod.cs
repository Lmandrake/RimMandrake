using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DieAfterPeriod : CompProperties
{
	public int timeToDieInTicks = 1000;

	public bool justVanish;

	public bool effect;

	public string effectFilth = "Filth_Blood";

	public CompProperties_DieAfterPeriod()
	{
		base.compClass = typeof(CompDieAfterPeriod);
	}
}
