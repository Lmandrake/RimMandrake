using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_BuildPeriodically : CompProperties
{
	public string defOfBuilding = "";

	public int ticksToBuild = 1000;

	public int maxBuildingsPerMap = 10;

	public List<string> acceptedTerrains;

	public bool onlyOneExistingPerPawn;

	public bool checkForExistingEdifices;

	public bool ifBedAssignOwnership;

	public bool onlyTamed;

	public CompProperties_BuildPeriodically()
	{
		base.compClass = typeof(CompBuildPeriodically);
	}
}
