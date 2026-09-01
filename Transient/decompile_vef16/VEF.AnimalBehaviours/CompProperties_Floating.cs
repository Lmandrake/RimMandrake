using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Floating : CompProperties
{
	public bool isFloater;

	public bool canCrossWater;

	public CompProperties_Floating()
	{
		base.compClass = typeof(CompFloating);
	}
}
