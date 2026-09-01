using System.Collections.Generic;

namespace VEF.Maps;

public class TerrainCompProperties_HediffGiver : TerrainCompProperties
{
	public List<HediffData> hediffsForHumanlike;

	public List<HediffData> hediffsForAnimals;

	public TerrainCompProperties_HediffGiver()
	{
		compClass = typeof(TerrainCompHediffGiver);
	}
}
