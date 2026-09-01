using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Maps;

public class TerrainCompProperties_MoteSpawner : TerrainCompProperties
{
	public ThingDef moteDef;

	public IntRange tickInterval;

	public FloatRange size;

	public FloatRange rotationRate;

	public FloatRange velocityAngle;

	public FloatRange velocitySpeed;

	public Color instanceColor;

	public FloatRange reqTempRangeToSpawn;

	public List<IntRange> reqTimeRangeToSpawn;

	public bool enableSettingsSpawnFogOnHotSprings;

	public float spawnChance;

	public TerrainCompProperties_MoteSpawner()
	{
		compClass = typeof(TerrainComp_MoteSpawner);
	}
}
