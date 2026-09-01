using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_TerrainChanger : CompProperties
{
	public int checkingRate = 100;

	public string FirstStageTerrain = "";

	public string SecondStageTerrain = "";

	public bool doThirdStage;

	public string ThirdStageTerrain = "";

	public bool inRadius;

	public int radius = 2;

	public CompProperties_TerrainChanger()
	{
		base.compClass = typeof(CompTerrainChanger);
	}
}
