using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_DieAfterPeriod : HediffCompProperties
{
	public int timeToDieInTicks = 1000;

	public bool justVanish;

	public bool effect;

	public string effectFilth = "Filth_Blood";

	public string DescriptionLabel = "VEF_TimeToDie";

	public HediffCompProperties_DieAfterPeriod()
	{
		base.compClass = typeof(HediffComp_DieAfterPeriod);
	}
}
