using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_GraphicByTerrain : CompProperties
{
	public int changeGraphicsInterval = 240;

	public List<string> terrains;

	public List<string> suffix;

	public List<string> hediffToApply;

	public bool waterOverride;

	public string waterSuffix = "_Winter";

	public string waterHediffToApply = "";

	public int waterSeasonalItemsIndex;

	public bool lowTemperatureOverride;

	public int temperatureThreshold = -10;

	public string lowTemperatureSuffix = "_Winter";

	public string lowTemperatureHediffToApply = "";

	public int lowTemperatureSeasonalItemsIndex;

	public bool snowOverride;

	public string snowySuffix = "_Winter";

	public string snowyHediffToApply = "";

	public int snowySeasonalItemsIndex;

	public bool provideSeasonalItems;

	public List<int> seasonalItemsIndexes;

	public CompProperties_GraphicByTerrain()
	{
		base.compClass = typeof(CompGraphicByTerrain);
	}
}
