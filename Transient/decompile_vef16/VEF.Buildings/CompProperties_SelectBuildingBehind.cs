using Verse;

namespace VEF.Buildings;

public class CompProperties_SelectBuildingBehind : CompProperties
{
	public string buildingToSelect;

	public string commandButtonImage = "";

	public string commandButtonText = "";

	public string commandButtonDesc = "";

	public CompProperties_SelectBuildingBehind()
	{
		base.compClass = typeof(CompSelectBuildingBehind);
	}
}
