using Verse;

namespace VEF.Buildings;

public class CompProperties_MountableOnWall : CompProperties
{
	public CompProperties_MountableOnWall()
	{
		base.compClass = typeof(CompMountableOnWall);
	}
}
