using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_NoTamingDecay : CompProperties
{
	public CompProperties_NoTamingDecay()
	{
		base.compClass = typeof(CompNoTamingDecay);
	}
}
