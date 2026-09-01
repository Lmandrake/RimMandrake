using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_MoteReleaser : CompProperties
{
	public ThingDef moteDef;

	public CompProperties_MoteReleaser()
	{
		base.compClass = typeof(CompMoteReleaser);
	}
}
