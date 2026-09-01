using System.Collections.Generic;
using KCSG;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class TileMutatorExtension : DefModExtension
{
	public List<PawnKindDefAndChance> forcedPawnKindDefs;

	public ThingDef thingToSpawn;

	public IntRange thingToSpawnAmount;

	public List<TerrainDef> terrainValidation;

	public bool allowWater = true;

	public List<PrefabDef> prefabsToSpawn;

	public IntRange prefabsToSpawnAmount = new IntRange(1, 1);

	public int minSeparationBetweenPrefabs = 10;

	public List<StructureLayoutDef> KCSGStructuresToSpawn;

	public IntRange KCSGStructuresToSpawnAmount = new IntRange(1, 1);

	public int minSeparationBetweenKCSGStructures = 10;

	public TerrainDef terrainToSwap;

	public TerrainDef terrainToSwapTo;

	public int mapSizeOverrideX = -1;

	public int mapSizeOverrideZ = -1;

	public float mapSizeMultiplier = 1f;

	public float deepOresMultiplier = 1f;

	public float diseaseMTBMultiplier = 1f;

	public float movementDifficultyOffset;

	public int riverbankSizeMultiplier = 1;

	public List<PlantsWithCommonality> plantDefsWithCommonality;

	public int extraDeepHelixienGasDeposits;

	public float tideStrengthMultiplier = 1f;
}
