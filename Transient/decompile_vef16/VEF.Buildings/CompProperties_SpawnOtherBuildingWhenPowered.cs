using Verse;

namespace VEF.Buildings;

public class CompProperties_SpawnOtherBuildingWhenPowered : CompProperties
{
	public string defOfBuildingToSpawn = "HorseshoesPin";

	public int tickRaresToCheck = 1;

	public CompProperties_SpawnOtherBuildingWhenPowered()
	{
		base.compClass = typeof(CompSpawnOtherBuildingWhenPowered);
	}
}
