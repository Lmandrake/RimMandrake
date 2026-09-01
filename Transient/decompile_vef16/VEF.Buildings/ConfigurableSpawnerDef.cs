using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class ConfigurableSpawnerDef : Def
{
	public List<string> items;

	public List<TerrainDef> allowedTerrains;

	public string listName;

	public string building;

	public string GizmoIcon = "";

	public string GizmoLabel = "";

	public string GizmoDescription = "";

	public int timeInTicks = 1000;

	public IntRange? timeInterval;
}
