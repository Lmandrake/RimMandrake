using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Maps;

public class ActiveTerrainDef : TerrainDef
{
	public List<TerrainCompProperties> terrainComps = new List<TerrainCompProperties>();

	public Type terrainInstanceClass = typeof(TerrainInstance);

	public TickerType tickerType;

	public T GetCompProperties<T>() where T : TerrainCompProperties
	{
		for (int i = 0; i < terrainComps.Count; i++)
		{
			if (terrainComps[i] is T result)
			{
				return result;
			}
		}
		return null;
	}
}
