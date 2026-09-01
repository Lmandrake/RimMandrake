using Verse;

namespace VEF.Buildings;

public class CompProperties_BouncingArrow : CompProperties
{
	public bool startBouncingArrowUponSpawning;

	public CompProperties_BouncingArrow()
	{
		base.compClass = typeof(CompBouncingArrow);
	}
}
