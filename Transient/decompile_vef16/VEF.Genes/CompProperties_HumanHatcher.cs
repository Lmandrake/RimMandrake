using Verse;

namespace VEF.Genes;

public class CompProperties_HumanHatcher : CompProperties
{
	public float hatcherDaystoHatch = 1f;

	public CompProperties_HumanHatcher()
	{
		base.compClass = typeof(CompHumanHatcher);
	}
}
