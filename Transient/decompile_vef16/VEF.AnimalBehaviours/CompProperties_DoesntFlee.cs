using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DoesntFlee : CompProperties
{
	public CompProperties_DoesntFlee()
	{
		base.compClass = typeof(CompDoesntFlee);
	}
}
