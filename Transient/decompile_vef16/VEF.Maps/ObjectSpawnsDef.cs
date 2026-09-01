using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class ObjectSpawnsDef : Def
{
	public ThingDef thingDef;

	public List<ThingOption> thingDefs;

	public ThingCategoryDef category;

	public PawnKindDef pawnKindDef;

	public FactionDef factionDef;

	public bool allowOnWater;

	public bool allowOnChunks;

	public IntRange numberToSpawn;

	public List<string> allowedTerrains;

	public List<string> disallowedTerrainTags;

	public List<BiomeDef> allowedBiomes;

	public List<RoadDef> allowedRoads;

	public bool findCellsOutsideColony;

	public bool spawnOnlyInPlayerMaps;

	public bool randomRotation;

	public bool allowSpawningOnPocketMaps;

	public List<PlanetLayerDef> allowedPlanetLayers;
}
