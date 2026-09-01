using System.Collections.Generic;
using Verse;

namespace VEF.Storyteller;

public class StructurePatternOffset
{
	public string pattern;

	public IntVec3 offset;

	public IntRange count = new IntRange(1, 1);

	public bool scatter;

	public int radialCount;

	public float radialDistance;

	public bool faceCenter;

	public bool randomRotated;

	public int rotationOffset;

	public bool putAnywhere;

	public List<PawnSpawnOption> spawnPawns;

	public List<ThingSpawnOption> spawnThings;

	public bool forceSpawnEnemiesIndoor;

	public bool unwaveringlyLoyal;

	public List<ThingDef> weapons;

	public FloatRange? pointsRange;
}
