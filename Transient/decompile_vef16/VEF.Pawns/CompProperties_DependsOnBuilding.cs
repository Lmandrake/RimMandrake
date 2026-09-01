using Verse;

namespace VEF.Pawns;

public class CompProperties_DependsOnBuilding : CompProperties
{
	public CompProperties_DependsOnBuilding()
	{
		base.compClass = typeof(CompPawnDependsOn);
	}
}
