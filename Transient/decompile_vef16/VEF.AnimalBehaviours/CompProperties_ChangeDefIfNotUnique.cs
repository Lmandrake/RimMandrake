using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_ChangeDefIfNotUnique : CompProperties
{
	public string defToChangeTo = "";

	public CompProperties_ChangeDefIfNotUnique()
	{
		base.compClass = typeof(CompChangeDefIfNotUnique);
	}
}
